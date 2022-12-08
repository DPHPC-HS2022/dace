#https://www.geeksforgeeks.org/merge-sort/
import dace as dc

N = dc.symbol('N')

@dc.program
def mergesort(arr: dc.float64[N]):
    if len(arr) > 1:
        mid = len(arr)//2
        # Dividing the array elements
        L = arr[:mid]

        # into 2 halves
        R = arr[mid:]

    # Sorting the first half
        mergesort(L)

    # Sorting the second half
        mergesort(R)

        i = j = k = 0

    # Copy data to temp arrays L[] and R[]
        while i < len(L) and j < len(R):
            if L[i] <= R[j]:
                arr[k] = L[i]
                i += 1
            else:
                arr[k] = R[j]
                j += 1
                k += 1

        # Checking if any element was left
        while i < len(L):
            arr[k] = L[i]
            i += 1
            k += 1

        while j < len(R):
            arr[k] = R[j]
            j += 1
            k += 1