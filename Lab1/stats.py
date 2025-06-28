def mean(numbers):
    return sum(numbers) / len(numbers) if numbers else 0

def median(numbers):
    sorted_nums = sorted(numbers)
    n = len(sorted_nums)
    if n == 0:
        return 0
    mid = n // 2
    if n % 2 == 0:
        return (sorted_nums[mid - 1] + sorted_nums[mid]) / 2
    else:
        return sorted_nums[mid]

def mode(numbers):
    if not numbers:
        return None
    frequency = {}
    for num in numbers:
        frequency[num] = frequency.get(num, 0) + 1
    max_freq = max(frequency.values())
    modes = [num for num, freq in frequency.items() if freq == max_freq]
    return modes[0] if len(modes) == 1 else modes

if __name__ == "__main__":
    print("Enter numbers separated by spaces:")
    try:
        user_input = input()
        number_list = [float(num) for num in user_input.split()]
        
        print("Mean:", mean(number_list))
        print("Median:", median(number_list))
        print("Mode:", mode(number_list))
    except ValueError:
        print("Please enter valid numbers only.")
