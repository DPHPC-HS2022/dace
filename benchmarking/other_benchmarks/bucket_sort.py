#https://www.geeksforgeeks.org/bucket-sort-2/
import dace as dc

N = dc.symbol('N')
			
def bucketSort(x: dc.float64[N]):
	arr = []
	slot_num = 10 # 10 means 10 slots, each
				# slot's size is 0.1
	for i in range(slot_num):
		arr.append([])
		
	# Put array elements in different buckets
	for j in x:
		index_b = int(slot_num * j)
		arr[index_b].append(j)
	
	# Sort individual buckets
	for i in range(slot_num):
		for i in range(1, len(arr[i])):
			up = b[arr[i]]
			j = i - 1
			while j >= 0 and arr[i][j] > up:
				arr[i][j + 1] = arr[i][j]
				j -= 1
			arr[i][j + 1] = up
		
	# concatenate the result
	k = 0
	for i in range(slot_num):
		for j in range(len(arr[i])):
			x[k] = arr[i][j]
			k += 1
	return x

