"""
File: student.py
Resources to manage a student's name and test scores.
"""
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

    # Comparison methods based on student name
    def __eq__(self, other):
        """Returns True if student names are equal."""
        return self.name == other.name

    def __lt__(self, other):
        """Returns True if this student's name is less than the other."""
        return self.name < other.name

    def __ge__(self, other):
        """Returns True if this student's name is greater than or equal to the other."""
        return self.name >= other.name

def main():
    """A simple test."""
    student1 = Student("Alice", 5)
    student2 = Student("Bob", 5)

    print("Initial students:")
    print(student1)
    print(student2)

    # Set scores
    for i in range(1, 6):
        student1.setScore(i, 100)
        student2.setScore(i, 30)

    print("\nUpdated students:")
    print(student1)
    print(student2)

    # Comparison testing
    print("\nComparison Results:")
    print(f"{student1.getName()} == {student2.getName()}? {student1 == student2}")
    print(f"{student1.getName()} < {student2.getName()}? {student1 < student2}")
    print(f"{student1.getName()} >= {student2.getName()}? {student1 >= student2}")

if __name__ == "__main__":
    main()
