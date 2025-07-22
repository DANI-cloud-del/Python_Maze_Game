from utils.settings import CELL_SIZE, PATH_WIDTH

class Collision:
    @staticmethod
    def check_player_wall_collision(rect, maze):
        grid_x = rect.centerx // CELL_SIZE
        grid_y = rect.centery // CELL_SIZE
        
        if not (0 <= grid_x < maze.cols and 0 <= grid_y < maze.rows):
            return True
            
        cell = maze.grid[grid_x][grid_y]
        
        margin = (CELL_SIZE - PATH_WIDTH)//2
        if (cell.walls['left'] and rect.left < grid_x * CELL_SIZE + margin) or \
           (cell.walls['right'] and rect.right > (grid_x+1) * CELL_SIZE - margin) or \
           (cell.walls['top'] and rect.top < grid_y * CELL_SIZE + margin) or \
           (cell.walls['bottom'] and rect.bottom > (grid_y+1) * CELL_SIZE - margin):
            return True
            
        return False
    
    @staticmethod
    def can_move(maze, x, y, direction):
        if not (0 <= x < maze.cols and 0 <= y < maze.rows):
            return False
            
        cell = maze.grid[x][y]
        
        if direction == (-1, 0):
            return not cell.walls['left']
        elif direction == (1, 0):
            return not cell.walls['right']
        elif direction == (0, -1):
            return not cell.walls['top']
        elif direction == (0, 1):
            return not cell.walls['bottom']
            
        return False