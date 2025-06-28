"""
File: stats.py
Prints the mode, median, and mean of a set of numbers in a file.
"""


fileName = input("Enter the file name: ")
f = open(fileName, 'r')


# Input the text, convert it to numbers, and
# add the numbers to a list
numbers = []
for line in f:
   words = line.split()
   for word in words:
       try:
           numbers.append(float(word))
       except ValueError:
           continue


# Define mean function
def mean(numbers):
   if not numbers:
       return 0
   return sum(numbers) / len(numbers)


# If the list is empty, print 0 for all
if not numbers:
   print("The mean is 0")
   print("The median is 0")
   print("The mode is 0")
else:
   # Sort the list and print the number at its midpoint
   numbers.sort()
   print("The mean is", mean(numbers))


   midpoint = len(numbers) // 2
   print("The median is", end=" ")
   if len(numbers) % 2 == 1:
       print(numbers[midpoint])
   else:
       print((numbers[midpoint] + numbers[midpoint - 1]) / 2)


   # Obtain the set of unique words and their
   # frequencies, saving these associations in
   # a dictionary
   theDictionary = {}
   for number in numbers:
       count = theDictionary.get(number, None)
       if count == None:
           theDictionary[number] = 1
       else:
           theDictionary[number] = count + 1


   # Find the mode by obtaining the maximum value
   # in the dictionary and determining its key
   theMaximum = max(theDictionary.values())
   for key in theDictionary:
       if theDictionary[key] == theMaximum:
           print("The mode is", key)
           break



