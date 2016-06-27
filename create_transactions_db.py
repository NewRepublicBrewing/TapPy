import tappy_sql_connection
from os import listdir
import string

tappy_sql_connection.cur.execute(" CREATE TABLE transactions \
    (unique_order_id TEXT PRIMARY KEY, salesvu_order_id INT, customer TEXT, \
     month INT, day INT, year INT, hour INT,\
     minute INT, ampm VARCHAR(2), product_array text[], subtotal REAL,\
     tax REAL, gratuity REAL, grand_total REAL);")

folder = '/Users/jimmy/Downloads/NRB_HTML_SALES/'
filenames = listdir(folder)
for index, file in enumerate(filenames):
    filenames[index] = (folder+filenames[index])
files_array = filenames

for file in files_array:
	unique_order_id = 'dummy'
	new_order = 'no'
	line_counter = 0
	order_counter = 0
	total_counter = 0
	product_line_counter = 1000
	subtotal_line_counter = 1000
	tax_line_counter = 1000
	gratuity_line_counter = 1000
	customer = 'cash'
	subtotal = 0
	tax = 0
	gratuity = 0
	grand_total = 0
	product_array = []
	#f = open('/Users/jimmy/Downloads/NRB_HTML_SALES/sept_2013.html')
	f = open(file)
	for line in iter(f):
		line_counter +=1
		#print(line.translate(None, string.whitespace))
		if line.translate(None, string.whitespace)[:106] == '<strongstyle="font-size:14px;font-weight:bold;font-family:TrebuchetMS,Helvetica,sans-serif,Arial;">OrderID':
			#Write out the old stuff
			if order_counter > 0:
				#This is working now, but wicked wicked slow...
				#temp_df = pd.DataFrame([[unique_order_id, salesvu_order_id, customer, month, day, year, hour, minute, ampm, product_array, subtotal, tax, gratuity, grand_total]], columns=['unique_order_id', 'salesvu_order_id', 'customer', 'month', 'day', 'year', 'hour', 'minute', 'ampm', 'product_array', 'subtotal', 'tax', 'gratuity', 'grand_total'])
				#indexed_temp_df = temp_df.set_index('unique_order_id')
				#individual_sales_df = individual_sales_df.append(indexed_temp_df)
				number_of_purchases = len(product_array)
				number_of_elements_in_line = 4#len(product_array[0])
				product_list_counter = 0
				sql_compatible_product_array = '{'
				for product_line in product_array:
					line_element_counter = 0
					product_list_counter += 1
					sql_compatible_product_array += '{'
					for element in product_line:
						line_element_counter += 1
						sql_compatible_product_array+=str(element)
						if line_element_counter != number_of_elements_in_line:
							sql_compatible_product_array+=','
					if product_list_counter != number_of_purchases:
						sql_compatible_product_array+='},'
					if product_list_counter == number_of_purchases:
						sql_compatible_product_array+='}'
				sql_compatible_product_array+='}'
				query = 'INSERT INTO transactions (unique_order_id, salesvu_order_id, customer, month, day, year, hour, \
						minute, ampm, product_array, subtotal, tax, gratuity, grand_total) VALUES (%s, %s, %s, %s, \
						%s, %s, %s, %s, %s, %s, %s, %s, %s, %s);'
				data=( unique_order_id, int(salesvu_order_id), customer, int(month), int(day), \
						int(year), int(hour), int(minute), ampm, sql_compatible_product_array, float(subtotal), float(tax), float(gratuity), float(grand_total))
				try:
					tappy_sql_connection.cur.execute(query,data)
					tappy_sql_connection.conn.commit()
				except:
					tappy_sql_connection.conn.rollback()
					#print('Duplicate entry found for order id:',unique_order_id)
					#print(data)
					#data=( unique_order_id+'dupe', int(salesvu_order_id), customer, int(month), int(day), \
					#    int(year), int(hour), int(minute), ampm, sql_compatible_product_array, float(subtotal), float(tax), float(gratuity), float(grand_total))
					#cur.execute(query,data)
					#conn.commit()
			#Reset values that need to be reset manually between orders
			customer = 'cash'
			product_array = []
			gratuity = 0
			#increase the order counter
			order_counter += 1
		if len(line.split('>')) > 1:
			order_id_check = (line.split('>')[1])[:9]
			if order_id_check == 'Order ID:':
				salesvu_order_id = (line.split('>')[2])[:-6]
				#print(order_id_check + ' '+ salesvu_order_id)
		if len(line.split('>')) > 2:
			order_time_check = (line.split('>')[2])[:11]
			if order_time_check == 'Order Time:':
				#print((line.split('>'))[3])
				month = ((line.split('>'))[3])[:2]
				day = ((line.split('>'))[3])[3:5]
				year = ((line.split('>'))[3])[6:10]
				hour = ((line.split('>'))[3])[11:13]
				minute = ((line.split('>'))[3])[14:16]
				ampm = ((line.split('>'))[3])[17:19]
				unique_order_id = salesvu_order_id+'_'+month+day+year+hour+minute

		if (line.translate(None, string.whitespace))[:145] == '<tdwidth="34%"style="background:#fff;padding:5px;font-size:14px;font-weight:bold;font-family:TrebuchetMS,Helvetica,sans-serif,Arial;"colspan="2">':
			product = (line.translate(None, string.whitespace)[145:-5])
			product_line_counter = 0
		product_line_counter += 1
		if product_line_counter == 2:
			unit_price = float((line.split('$')[1])[1:-7])
		if product_line_counter == 3:
			quantity = int(((line.split('>'))[1])[:-4])
		if product_line_counter == 4:
			total = float((line.split('$')[1])[1:-7])
		if product_line_counter == 5:
			product_line = [product, unit_price, quantity, total]
			product_array.append(product_line)
		if len(line.split('title')) == 2:
			#print(len(line.split('title')))
			customer = line.split('"')[5]
		#print('Customer: '+customer)
		if (line.translate(None, string.whitespace))[:145] == '<tdwidth="58%"style="padding:5px0px;font-family:TrebuchetMS,Helvetica,sans-serif,Arial;">Subtotal</td>':
			subtotal_line_counter = 0
			#print((line.translate(None, string.whitespace)))
		subtotal_line_counter += 1
		if subtotal_line_counter == 2:
			subtotal = float((((line.split('$')[1])[1:-13])))
			#print('subtotal: '+subtotal)
		if (line.translate(None, string.whitespace))[:145] == '<tdwidth="58%"style="padding:5px0px;font-family:TrebuchetMS,Helvetica,sans-serif,Arial;">Tax</td>':
			tax_line_counter = 0
		tax_line_counter += 1
		if tax_line_counter == 2:
			tax = float((line.split('>')[1])[2:-4])
			#print('tax: '+tax)
		if (line.translate(None, string.whitespace))[:145] == '<tdwidth="58%"style="padding:5px0px;font-family:TrebuchetMS,Helvetica,sans-serif,Arial;">Gratuity</td>':
			gratuity_line_counter = 0
		gratuity_line_counter += 1
		if gratuity_line_counter == 2:
			gratuity = float((line.translate(None, string.whitespace))[106:-5])
			#print('gratuity: '+gratuity)
		if (line.translate(None, string.whitespace))[:184] == '<tdwidth="41%"align="right"style="padding:5px5px;font-family:TrebuchetMS,Helvetica,sans-serif,Arial;"><strongstyle="font-size:14px;font-family:TrebuchetMS,Helvetica,sans-serif,Arial;">':
			grand_total = float((line.translate(None, string.whitespace))[185:-14])
		if line_counter == -1:
			break
	f.close()
	print('Orders read in: '+str(order_counter)+' from '+file)