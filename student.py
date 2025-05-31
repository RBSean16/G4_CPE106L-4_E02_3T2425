import random

class Student(object):
    """Represents a student."""

    def __init__(self, name, number):
        """All scores are initially 0."""
        self.name = name
        self.scores = [0] * number

    def getName(self):
        """Returns the student's name."""
        return self.name

    def setScore(self, i, score):
        """Resets the ith score, counting from 1."""
        self.scores[i - 1] = score

    def getScore(self, i):
        """Returns the ith score, counting from 1."""
        return self.scores[i - 1]

    def getAverageScore(self):
        """Returns the average score."""
        return sum(self.scores) / len(self.scores)

    def getHighScore(self):
        """Returns the highest score."""
        return max(self.scores)

    def __str__(self):
        """Returns the string representation of the student."""
        return f"Name: {self.name}\nScores: {' '.join(map(str, self.scores))}"

    def __lt__(self, other):
        """Compares students based on names for sorting."""
        return self.name < other.name

def main():
    """Creates several students, shuffles them, sorts them, and displays their information."""
    
    # Creating a list of Student objects
    students = [
        Student("Alice", 3),
        Student("Bob", 3),
        Student("Charlie", 3),
        Student("Dave", 3),
        Student("Eve", 3)
    ]

    # Assign random scores to each student
    for student in students:
        for i in range(1, 4):
            student.setScore(i, random.randint(60, 100))

    # Shuffle the list
    random.shuffle(students)
    
    print("Shuffled List:")
    for student in students:
        print(student)

    # Sort the students by name
    students.sort()

    print("\nSorted List:")
    for student in students:
        print(student)

if __name__ == "__main__":
    main()
