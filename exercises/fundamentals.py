"""Runnable examples for Day 2 Python fundamentals."""


def grade_for(mark):
    """Return a simple letter grade after validating the input mark."""
    if not isinstance(mark, (int, float)) or isinstance(mark, bool) or not 0 <= mark <= 100:
        raise ValueError("Mark must be a number from 0 through 100.")
    if mark >= 90:
        return "A"
    if mark >= 80:
        return "B"
    if mark >= 70:
        return "C"
    if mark >= 60:
        return "D"
    return "F"


def main():
    # Variables, primitive types, and operators.
    trainee = "Pug Arch Intern"
    passing_mark = 60
    marks = [92, 78, 85, 58]

    # Lists, tuples, sets, and dictionaries.
    mark_tuple = tuple(marks)
    unique_marks = set(mark_tuple)
    grades = {mark: grade_for(mark) for mark in unique_marks}

    # Loop, conditional, function, and list comprehension.
    passed = [mark for mark in marks if mark >= passing_mark]
    average = sum(marks) / len(marks)
    describe = lambda mark: f"{mark}: {grade_for(mark)}"

    print(f"{trainee}: marks={marks}; unique={len(unique_marks)}")
    print(f"Passed marks: {passed}; average={average:.2f}")
    print("Grade lookup:", grades)
    print("Examples:", "; ".join(describe(mark) for mark in marks))

    # Exception handling for invalid user input.
    raw = input("Try a mark from 0 to 100: ").strip()
    try:
        print(f"Grade: {grade_for(float(raw))}")
    except ValueError as exc:
        print(f"Invalid mark: {exc}")


if __name__ == "__main__":
    main()
