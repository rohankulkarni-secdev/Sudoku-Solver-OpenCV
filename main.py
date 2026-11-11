import numpy as np
import cv2
import os, shutil
import scipy

image_path = "./board"
cell_path = "./cells"

if os.path.isdir(cell_path):
    shutil.rmtree(cell_path)
    os.mkdir(cell_path)
else:
    os.mkdir(cell_path)

image = cv2.imread('sudoku.webp')
image_area = (image.shape[0] * image.shape[1])  #calculate precise perimeter for comparison later

#convert to grayscale
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

#blur to average pixels
blur = cv2.GaussianBlur(gray, (5,5), 0)

#edge detection (brightness difference)
canny = cv2.Canny(blur, 20, 150)

#contour detection (shapes) and then white line 
contour, temp = cv2.findContours(canny, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE) #outermost shapes and compression


#sort by area, largest first
contours = sorted(contour, key=cv2.contourArea, reverse=True)
board_contour = None

#finding the board amongst other shapes
for c in contours:
    #calculate perimeter of shapes
    perimeter = cv2.arcLength(c,True) #look for closed shapes, hence True

    approx = cv2.approxPolyDP(c, 0.02*perimeter, True) #approximate shape (messy lines = full shape) 0.02 is precision value, simplest shape possible, here thats square
    #if the shape has exactly 4 corners, square, board found (already found it to be the largest area)
    if len(approx) == 4:
        area = cv2.contourArea(c)
        if area > image_area * 0.2:
            print("Found board")
            board_contour = approx
            break



    #Dont continue so we dont overwrite the board contour

if board_contour is not None:
    #drawing green line around board, of particular thickness (3)
    cv2.drawContours(image, [board_contour], -1 , (0,255,0),3) # -1 is contour index in the list
    print("Board located.")
    #cords of bounding box
    x, y, w, h = cv2.boundingRect(board_contour)

    #cropping, x and y are top left corner
    crop = image[y:y+h, x:x+w]

    #calculating size of each of the 81 cells
    cell_height = h//9
    cell_width = w//9

    #slicing board
    for r in range(9):
        for c in range(9):
            start_y = r*cell_height
            end_y = start_y + cell_height
            start_x = c*cell_width
            end_x = start_x + cell_width

            #slicing to that cell
            cell = crop[start_y:end_y, start_x:end_x]
            cv2.imwrite(f"{cell_path}/cell_{r}_{c}.png", cell)
            
else:
    print("Board not found, try adjusting values.")


#Backtracking basic example
def combinations(nums, current_combo, result):
    if len(current_combo) == 2:
        result.append(list(current_combo))
        return 
    
    for num in nums:
        current_combo.append(num)
        combinations(nums, current_combo, result)

        current_combo.pop()


#Check Conditions
def check(matrix, r, c, n):
    #check row:
    for i in range(9):
        if matrix[r][i] == n:
            return False

    #check col:
    for i in range(9):
        if matrix[i][c] == n:
            return False

    #check 3x3 box:
    top_left_r = r - r%3 #how many rows from top
    top_left_c = c - c%3 #how many cols from left

    for i in range(3):
        for j in range(3):
            if matrix[top_left_r+i][top_left_c+j] == n:
                return False
    return True
    
def board_validity(sudoku_matrix):
    for r in range(9):
        for c in range(9):
            k = sudoku_matrix[r][c]

            sudoku_matrix[r][c] = 0

            if check(sudoku_matrix, r, c, k):
                sudoku_matrix[r][c] = k
                return True
            else:
                return False

        return True
            



def solve_board(sudoku_matrix):
    for r in range(9):
        for c in range(9):
            if sudoku_matrix[r][c] == 0:
                for k in range(1,10):
                    if check(sudoku_matrix, r, c, k):
                        sudoku_matrix[r][c] = k

                        if solve_board(sudoku_matrix):
                            return True
                        sudoku_matrix[r][c] = 0

                return False
            
    return board_validity(sudoku_matrix)    


sample_board = [
    [5, 3, 0, 0, 7, 0, 0, 0, 0],
    [6, 0, 0, 1, 9, 5, 0, 0, 0],
    [0, 9, 8, 0, 0, 0, 0, 6, 0],
    [8, 0, 0, 0, 6, 0, 0, 0, 3],
    [4, 0, 0, 8, 0, 3, 0, 0, 1],
    [7, 0, 0, 0, 2, 0, 0, 0, 6],
    [0, 6, 0, 0, 0, 0, 2, 8, 0],
    [0, 0, 0, 4, 1, 9, 0, 0, 5],
    [0, 0, 0, 0, 8, 0, 0, 7, 9]
]



