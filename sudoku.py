import copy
from collections import Counter

# Defining a custom Exception class named "SudokuError"
class SudokuError(Exception):
    # The constructor method for the SudokuError class
    def __init__(self, message):
        # The error message to be displayed when this exception is raised
        self.message = message



class Sudoku:
    def __init__(self, file_name):
        # Open the input file
        with open(file_name) as file:
            # Remove unnecessary spaces and empty lines from the file's lines
            clean_data = [' '.join(item.split()) for item in file.readlines() if item.strip() != '']
            numeric_data = []
            self.file_name = file_name
            # Convert each line to a list of integers
            for line in clean_data:
                split_line = line.split()
                try:
                    if len(split_line) == 1:  # If the line is a single string of digits (no spaces)
                        numeric_line = list(map(int, list(split_line[0])))  # Convert each character to an integer
                    else:  # If there are spaces in the line
                        numeric_line = list(map(int, split_line))  # Convert each string to an integer
                except ValueError:
                    # If conversion to int fails, raise an error
                    raise SudokuError("Incorrect input")

                if len(numeric_line) != 9:  # Check if each line contains 9 numbers
                    raise SudokuError("Incorrect input")

                numeric_data.append(numeric_line)  # Add the processed line to the numeric_data list

            if len(numeric_data) != 9:  # Check if there are 9 lines
                raise SudokuError("Incorrect input")

            self.original = numeric_data  # Save the processed 9x9 grid to self.original

        # Create a copy of the rows and save it to self.rows
        rows = self.original.copy()
        self.rows = rows

        # Transpose the grid to get the columns and save them to self.cols
        cols = [list(col) for col in zip(*self.original)]
        self.cols = cols

        # Extract the 3x3 boxes and save them to self.boxes
        boxes = []
        for i in range(0, 9, 3):
            for j in range(0, 9, 3):
                box = []
                for x in range(i, i + 3):
                    for y in range(j, j + 3):
                        box.append(self.original[x][y])
                boxes.append(box)
        self.boxes = boxes

    def preassess(self):
        # If all checks pass (i.e., there are no repeated numbers in any row, column, or box),
        if (self.check_sudoku(self.rows)
                and self.check_sudoku(self.cols)
                and self.check_sudoku(self.boxes)):
            # Print a positive message
            print("There might be a solution.")
        else:
            # If any check fails (i.e., there are repeated numbers in any row, column, or box),
            # Print a negative message
            print("There is clearly no solution.")

    def check_sudoku(self, grid):
        # Iterate through each row in the grid
        for row in grid:
            # Create a new list that only contains non-zero elements
            row = [num for num in row if num != 0]
            # Check for any duplicate elements. If the size of the set (which only contains unique elements)
            # is less than the size of the list, then there are duplicate elements.
            if len(set(row)) < len(row):
                return False  # Returns False if any duplicates are found
        return True  # Returns True if no duplicates are found, i.e., the grid passed the check

    def bare_tex_output(self):
        file_name = self.file_name[: -4] + "_bare.tex"
        self.convert_latex(file_name, self.original)

    def convert_latex(self, file_name, grid, marked=None, marked_in_worked=None):
        with open(file_name, 'w') as file:
            # Define the beginning of the LaTeX document
            head_format = '''\\documentclass[10pt]{article}
\\usepackage[left=0pt,right=0pt]{geometry}
\\usepackage{tikz}
\\usetikzlibrary{positioning}
\\usepackage{cancel}
\\pagestyle{empty}

\\newcommand{\\N}[5]{\\tikz{\\node[label=above left:{\\tiny #1},
                               label=above right:{\\tiny #2},
                               label=below left:{\\tiny #3},
                               label=below right:{\\tiny #4}]{#5};}}

\\begin{document}

\\tikzset{every node/.style={minimum size=.5cm}}

\\begin{center}
\\begin{tabular}{||@{}c@{}|@{}c@{}|@{}c@{}||@{}c@{}|@{}c@{}|@{}c@{}||@{}c@{}|@{}c@{}|@{}c@{}||}\\hline\\hline\n'''
            file.write(head_format)
            for i in range(len(grid)):  # Loop through each line in the grid
                file.write("% Line " + str(i + 1) + "\n")  # Comment to denote the beginning of a line
                if marked is None:  # If there are no cells to mark
                    file.write(self.fill_content(grid[i]))
                else:  # If there are cells to mark
                    if marked_in_worked is None:  # If there's no working grid
                        file.write(self.fill_content(grid[i], marked[i]))
                    else:  # If there's a working grid
                        file.write(self.fill_content(grid[i], marked[i], marked_in_worked[i]))

                if i % 3 == 2:  # Add a line after every three rows
                    file.write("\hline")
                file.write("\n")
                if i != 8:  # Don't add a newline after the last row
                    file.write("\n")
            # Define the end of the LaTeX document
            end_format = '''\end{tabular}
\end{center}

\end{document}
'''
            file.write(end_format)

    def fill_content(self, line, elements=None, marked_in_worked=None):
        content = ""  # Initialize an empty string to store the LaTeX commands for the row

        # Loop through each number in the line
        for i in range(len(line)):
            # If there are no elements to mark, add an empty node command
            if elements == None:
                content += "\\N{}{}{}{}"
            else:  # If there are elements to mark
                # Add a node command with labels for the numbers
                content += "\\N"
                # The small number are grouped into 4 groups: {1,2}, {3,4}, {5,6}, {7,8,9}
                for group in [sorted({1, 2}), sorted({3, 4}), sorted({5, 6}), sorted({7, 8, 9})]:
                    if marked_in_worked is None:
                        content += self.format_elements(elements[i], group)
                    else:
                        content += self.format_elements(elements[i], group, marked_in_worked[i])

            # If the cell is not empty, add the number in the center of the node
            if line[i] != 0:
                content += "{" + str(line[i]) + "}"
            else:  # If the cell is empty, add an empty center
                content += "{}"

            # If it's the end of the row, add a new line and a line below
            if i == 8:
                content += " \\\\ \\hline"
            else:  # If it's not the end of the row
                if (i + 1) % 3 != 0:  # If it's not the end of a 3x3 box, add a tab (&)
                    content += " & "
                else:  # If it's the end of a 3x3 box, add a new line and a tab
                    content += " &\n"

        return content  # Return the LaTeX commands for the row

    def create_force(self):
        self.force = copy.deepcopy(self.original)

        # Copy the original Sudoku grid to self.force
        self.force = copy.deepcopy(self.original)

        # Mark the possible numbers for each cell in self.force using the markup method
        self.markup()

        # Keep looping until no more numbers can be filled in
        while 1:
            # Use the status variable to track whether any numbers have been filled in during the current loop
            status = False

            # Loop through each cell in the Sudoku grid
            for x in range(len(self.force)):
                for y in range(len(self.force[x])):
                    # If a cell can only contain one number, fill in that number
                    if len((self.marked[x][y])) == 1:
                        self.force[x][y] = self.marked[x][y][0]
                        status = True  # Update the status to True since a number has been filled in
                        self.markup()  # Update the possible numbers for each cell

                    # If a cell can contain more than one number, but one of those numbers can only appear in this cell
                    # within its 3x3 box, then fill in that number
                    elif len((self.marked[x][y])) > 1:
                        box_cells = self.locate_box_cells(x, y)  # Get the cells in the same 3x3 box
                        marked_boxes = []  # Initialize an empty list to store the possible numbers for the cells in the box

                        # Add the possible numbers for each cell in the box to marked_boxes
                        for (i, j) in box_cells:
                            marked_boxes += self.marked[i][j]

                        # Count the occurrences of each number in marked_boxes
                        counter = Counter(marked_boxes)

                        # Get the numbers that only appear once in marked_boxes
                        single_occurrence_numbers = [number for number, count in counter.items() if count == 1]

                        # If a possible number for the current cell is a single occurrence number, fill in that number
                        for number in self.marked[x][y]:
                            if number in single_occurrence_numbers:
                                self.force[x][y] = number
                                status = True  # Update the status to True since a number has been filled in
                                self.markup()  # Update the possible numbers for each cell

            # If no more numbers can be filled in, break the loop
            if status == False:
                break


    def forced_tex_output(self):
        # Generate the output file name by replacing the input file extension with "_forced.tex"
        file_name = self.file_name[: -4] + "_forced.tex"
        self.create_force()
        # Generate the "forced" Sudoku grid in LaTeX format
        self.convert_latex(file_name, self.force)

    def markup(self):
        # Initialize an empty list to store the possible numbers for each cell
        self.marked = []
        # Loop through each cell in the Sudoku grid
        for x in range(len(self.force)):
            temp = []  # Initialize an empty list to store the possible numbers for the cells in the current row
            for y in range(len(self.force[x])):
                # If a cell is empty (contains 0), get the possible numbers for this cell using the possible_numbers method
                if self.force[x][y] == 0:
                    temp.append(self.possible_numbers(x, y))
                else:  # If a cell is not empty, add an empty list to temp
                    temp.append([])
            self.marked.append(temp)  # Add temp to self.marked

    def possible_numbers(self, x, y):
        # Initialize a set with numbers from 1 to 9
        numbers = {i for i in range(1, 10)}

        # Get the set of numbers in the same row as the cell
        rows = {self.force[x][i] for i in range(9)}

        # Get the set of numbers in the same column as the cell
        cols = {self.force[i][y] for i in range(9)}

        # Get the coordinates of the cells in the same box as the cell
        box_cells = self.locate_box_cells(x, y)

        # Get the set of numbers in the same box as the cell
        boxes = {self.force[i][j] for (i, j) in box_cells}

        # Return a sorted list of the numbers that are in 'numbers' but not in 'rows', 'cols', or 'boxes'
        return sorted(numbers - rows - cols - boxes)

    def marked_tex_output(self):
        file_name = self.file_name[: -4] + "_marked.tex"
        self.create_force()
        self.convert_latex(file_name, self.force, self.marked)

    @staticmethod
    def format_elements(elements, sorted_list, marked_in_worked=None):
        # Find the intersection of `sorted_list` and `elements` and sort it
        intersected = sorted(set(sorted_list) & set(elements))

        if marked_in_worked is not None:
            # Find the elements in `sorted_list` but not in `marked_in_worked` and sort it
            intersected_worked = sorted(set(sorted_list) - set(marked_in_worked))

            # For each element in `intersected`, if it's in `intersected_worked`,
            # replace it with LaTeX code to cancel it out;
            # otherwise, convert it to a string
            intersected = ['\\cancel{' + str(i) + '}' if i in intersected_worked else str(i) for i in intersected]

        # Return the LaTeX code to create a set of the `intersected` elements, with each element separated by a space
        return "{" + " ".join(map(str, intersected)) + "}"

    def locate_box(self, i, j):
        return (i // 3) * 3 + j // 3  # Return to Box Number

    def locate_box_cells(self, x, y):
        box_x, box_y = x // 3, y // 3  # Determine the coordinates of the box
        cells = [(i, j) for i in range(box_x * 3, (box_x + 1) * 3) for j in range(box_y * 3, (box_y + 1) * 3)]
        return cells

    def worked_tex_output(self):
        file_name = self.file_name[: -4] + "_worked.tex"
        self.create_force()
        self.markup()
        self.marked_in_worked = copy.deepcopy(self.marked)
        self.worked = copy.deepcopy(self.force)
        self.solve_sudoku()
        self.convert_latex(file_name, self.worked, self.marked, self.marked_in_worked)

    def update_cell(self, row_index, col_index):
        updated = False  # Initialize 'updated' to False, which checks if any update occurs in this function call.

        # If the cell in question has only one possible number, fill this number in the 'worked' grid.
        if len(self.marked_in_worked[row_index][col_index]) == 1:
            self.worked[row_index][col_index] = self.marked_in_worked[row_index][col_index][0]

            # Loop over all cells in the same row and column.
            for i in range(9):
                # If the filled number is in the possible numbers of the cell in the same row, remove it.
                if self.worked[row_index][col_index] in self.marked_in_worked[row_index][i]:
                    self.marked_in_worked[row_index][i] = list(
                        filter(lambda x: x != self.worked[row_index][col_index], self.marked_in_worked[row_index][i]))
                # If the filled number is in the possible numbers of the cell in the same column, remove it.
                for i in range(9):
                    if self.worked[row_index][col_index] in self.marked_in_worked[i][col_index]:
                        self.marked_in_worked[i][col_index] = list(
                            filter(lambda x: x != self.worked[row_index][col_index],
                                   self.marked_in_worked[i][col_index]))
                updated = True  # If a number is removed, the grid is updated. Set 'updated' to True.

            # Loop over all cells in the same box.
            for x_now, y_now in self.locate_box_cells(row_index, col_index):
                # If the filled number is in the possible numbers of the cell in the same box, remove it.
                if self.worked[row_index][col_index] in self.marked_in_worked[x_now][y_now]:
                    self.marked_in_worked[x_now][y_now] = list(
                        filter(lambda x: x != self.worked[row_index][col_index],
                               self.marked_in_worked[x_now][y_now]))
                updated = True  # If a number is removed, the grid is updated. Set 'updated' to True.

        return updated  # Return 'updated'. If it's True, it means the grid has been updated in this function call.

    def solve_sudoku(self):
        updated = False  # Initialize variable to track if grid was updated during this round.

        # For each cell, attempt to apply the preemptive set rule.
        for row_index in range(9):
            for col_index in range(9):
                if self.worked[row_index][col_index] == 0:
                    updated = self.preemptive_set(row_index, col_index) or updated

        # For each cell, attempt to update the cell if only one possible number is left.
        for row_index in range(9):
            for col_index in range(9):
                updated = self.update_cell(row_index, col_index) or updated

        # If the grid was updated during this round, call the function again.
        if updated:
            self.solve_sudoku()

    def remove_number_from_preemptive_set(self, coordinates, current_set):
        updated = False  # Initialize variable to track if grid was updated during this round.
        count = 0  # Counter for the number of cells that contain only numbers from the current set.

        # For each cell, if the possible numbers are a subset of current set, increase the counter.
        for i in coordinates:
            if self.worked[i[0]][i[1]] == 0:
                if set(self.marked_in_worked[i[0]][i[1]]) <= current_set:
                    count += 1

        # If the count equals the size of the current set, remove the numbers of the current set from other cells.
        if count == len(current_set):
            for i in coordinates:
                if self.worked[i[0]][i[1]] == 0 and not set(self.marked_in_worked[i[0]][i[1]]) <= current_set:
                    for number in current_set:
                        if number in self.marked_in_worked[i[0]][i[1]]:
                            self.marked_in_worked[i[0]][i[1]] = list(
                                filter(lambda x: x != number, self.marked_in_worked[i[0]][i[1]]))
                            updated = True  # The grid was updated.

        return updated  # Return if the grid was updated.

    def preemptive_set(self, row_index, col_index):
        # Gather the coordinates of the row, column and box.
        current_set = set(self.marked_in_worked[row_index][col_index])
        row_coordinates = [(row_index, i) for i in range(9)]
        column_coordinates = [(i, col_index) for i in range(9)]
        box_coordinates = self.locate_box_cells(row_index, col_index)

        # Attempt to remove numbers from the preemptive set in the row, column and box.
        row_updated = self.remove_number_from_preemptive_set(row_coordinates, current_set)
        col_updated = self.remove_number_from_preemptive_set(column_coordinates, current_set)
        box_updated = self.remove_number_from_preemptive_set(box_coordinates, current_set)

        return row_updated or col_updated or box_updated  # Return if any of the operations updated the grid.
