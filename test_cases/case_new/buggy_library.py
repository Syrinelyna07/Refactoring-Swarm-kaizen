import os
import json
import math


class GradeManager:
    """Manages a basic student grade system."""
    
    def __init__(self):
        """Initialize the grade manager with empty student records."""
        self.students = {}
        self.passing_grade = 10

    def add_student(self, name, grades):
        """Add a student with their grades.
        
        Args:
            name (str): Student name
            grades (list): List of numeric grades
        """
        if not isinstance(name, str) or not name.strip():
            raise ValueError("Name must be a non-empty string")
        if not isinstance(grades, list):
            raise ValueError("Grades must be a list")
        self.students[name] = grades

    def get_average(self, name):
        """Get the average grade for a student.
        
        Args:
            name (str): Student name
            
        Returns:
            float: Average grade
            
        Raises:
            KeyError: If student not found
            ValueError: If student has no grades
        """
        if name not in self.students:
            raise KeyError(f"Student '{name}' not found")
        grades = self.students[name]
        if len(grades) == 0:
            return 0.0
        total = 0
        for g in grades:
            total = total + g
        average = total / len(grades)
        return average

    def get_status(self, name):
        """Get the pass/fail status for a student.
        
        Args:
            name (str): Student name
            
        Returns:
            str: "Passed" or "Failed"
        """
        avg = self.get_average(name)
        if avg >= self.passing_grade:
            return "Passed"
        else:
            return "Failed"

    def top_student(self):
        """Find the student with the highest average grade.
        
        Returns:
            str or None: Name of top student, None if no students
        """
        if not self.students:
            return None
        best = None
        best_avg = -1
        for name in self.students:
            avg = self.get_average(name)
            if avg > best_avg:
                best_avg = avg
                best = name
        return best

    def remove_student(self, name):
        """Remove a student from the system.
        
        Args:
            name (str): Student name
            
        Raises:
            KeyError: If student not found
        """
        if name not in self.students:
            return
        del self.students[name]

    def export_results(self, filepath):
        """Export student results to a JSON file.
        
        Args:
            filepath (str): Path to output file
        """
        results = {}
        for name in self.students:
            results[name] = {
                "average": self.get_average(name),
                "status": self.get_status(name)
            }
        with open(filepath, "w") as f:
            json.dump(results, f)

    def get_grade_distribution(self, name):
        """Get grade distribution for a student.
        
        Args:
            name (str): Student name
            
        Returns:
            dict: Distribution of grades in ranges
        """
        if name not in self.students:
            raise KeyError(f"Student '{name}' not found")
        grades = self.students[name]
        below = 0
        average_range = 0
        above = 0
        for g in grades:
            if g < 10:
                below += 1
            elif g >= 10 and g <= 15:
                average_range += 1
            else:
                above += 1
        return {"below_10": below, "10_to_15": average_range, "above_15": above}

    def compute_std_deviation(self, name):
        """Compute standard deviation of a student's grades.
        
        Args:
            name (str): Student name
            
        Returns:
            float: Standard deviation
        """
        if name not in self.students:
            raise KeyError(f"Student '{name}' not found")
        grades = self.students[name]
        if len(grades) == 0:
            raise ValueError(f"Student '{name}' has no grades")
        avg = self.get_average(name)
        variance = sum((g - avg) ** 2 for g in grades) / len(grades)
        return math.sqrt(variance)


def load_from_csv(filepath):
    """Load student data from a CSV file.
    
    Args:
        filepath (str): Path to CSV file
        
    Returns:
        GradeManager: Populated grade manager
        
    Raises:
        FileNotFoundError: If file doesn't exist
        ValueError: If file format is invalid
    """
    manager = GradeManager()
    with open(filepath, "r") as f:
        lines = f.readlines()
    for line in lines:
        line = line.strip()
        if line == "":
            continue
        parts = line.split(",")
        name = parts[0]
        grades = []
        for i in range(1, len(parts)):
            try:
                grades.append(int(parts[i]))
            except ValueError:
                raise ValueError(f"Invalid grade value '{parts[i]}' for student '{name}'")
        manager.add_student(name, grades)
    return manager


def summarize(manager):
    """Print a summary of all student grades.
    
    Args:
        manager (GradeManager): Grade manager instance
    """
    print("=== Grade Summary ===")
    for name in manager.students:
        status = manager.get_status(name)
        print(f"{name} -> {status}")
    top = manager.top_student()
    print(f"Top student: {top}")