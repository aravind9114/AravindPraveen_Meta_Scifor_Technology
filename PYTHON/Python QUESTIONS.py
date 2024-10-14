# 1. Find sum of list elements
lst = [1,2,3,4,5]
total = sum(lst)
print("Total:",total)

# 2. Largest element in a list
lst = [1,2,3,4,5]
largest = max(lst)
print("Largest:",largest)

# 3. Remove Duplicates in a list
lst = [1,2,2,3,4,4,5]
lst = list(set(lst))
print("Duplicates Removed:",lst)

# 4. Check Uniqueness
lst = [1,2,3,4,4,5]
lst_2 = []
for num in lst:
    if num in lst_2:
        print("Not Unique")
        break
    lst_2.append(num)
else:
    print("Unique")


# 5. Program to reverse list
lst = [1,2,3,4,5]
lst = lst[::-1]
print('Reversed',lst)

# 6.count of odd and even
lst = [1,2,3,4,5]
odd = 0
even = 0
for num in lst:
    if num % 2 == 0:
        even += 1
    else:
        odd += 1
print('count of even:',even)
print('count of odd:',odd)

# 7. Check if a list is subset of another list
lst1 = [1,2,3]
lst2 = [1,2,3,4,5]
if set(lst1).issubset(set(lst2)):
    print("Subset")
else:
    print("not a Subset")

# 8. Max diff btw two consecutive elements in a list
lst = [10,9,12,15]
max_diff = lst[1] - lst[0]
for i in range(1, len(lst) - 1):
    diff = lst[i+1] - lst[i]
    if diff > max_diff:
        max_diff = diff
print("Max diff :",max_diff)

# 9. Merge Multiple dictionaries
dict1 = {'a':1,'b':2}
dict2 = {'b':3,'c':4}
merged_dict = dict1.copy()
merged_dict.update(dict2)
print("Merged:",merged_dict)

# 10. Find words frequency in a sentence
sentence = "I love Python Programming , Python is easy ."
words = sentence.split()
word_frequency = {}
for word in words:
    if word in word_frequency:
        word_frequency[word] += 1
    else:
        word_frequency[word] = 1
print(word_frequency)