data_arr = [1,2,4,5,7,8,9,10,56,57,59]

count = 0

def is_odd_number(input_number):
    if input_number % 2 == 1:
        return True
    else:
        return False


for element in data_arr:
    if is_odd_number(element):
        count += 1


print ("THe number of odd num: %s" % count)