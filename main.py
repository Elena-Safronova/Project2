from random import randint
# подгрузка модуля для генерации случайной раскладки доски на старте и ходов компьютера


# Параметры и свойства игровая точка
class Dot:
    def __init__(self, x, y):  # инициализация класса точка
        self.x = x
        self.y = y

    def __eq__(self, other):  # сравнение значений точек
        return self.x == other.x and self.y == other.y

    def __repr__(self):  # возвращение значения точки
        return f"({self.x}, {self.y})"


class BoardException(Exception):
    pass


# возврат проверки на действие в пределах игрового поля
class BoardOutException(BoardException):
    def __str__(self):
        return "Вы пытаетесь выстрелить за доску!"


# возврат проверки на повтор
class BoardUsedException(BoardException):
    def __str__(self):
        return "Вы уже стреляли в эту клетку"


class BoardWrongShipException(BoardException):
    pass


# Параметры и свойства корабля
class Ship:
    def __init__(self, bow, l, o):
        self.bow = bow
        self.l = l  # длина корабля
        self.o = o
        self.lives = l  # кол-во жизней у корабля

    @property
    def dots(self):  # расчет попадания
        ship_dots = []
        for i in range(self.l):
            cur_x = self.bow.x
            cur_y = self.bow.y

            if self.o == 0:
                cur_x += i

            elif self.o == 1:
                cur_y += i

            ship_dots.append(Dot(cur_x, cur_y))

        return ship_dots

    def shooten(self, shot):
        return shot in self.dots


# параметры и свойства корабля
class Board:
    def __init__(self, hid=False, size=6):
        self.size = size
        self.hid = hid

        self.count = 0

        self.field = [["O"] * size for _ in range(size)]

        self.busy = []
        self.ships = []

    def add_ship(self, ship):

        for d in ship.dots:
            if self.out(d) or d in self.busy:
                raise BoardWrongShipException()
        for d in ship.dots:
            self.field[d.x][d.y] = "■"
            self.busy.append(d)

        self.ships.append(ship)
        self.contour(ship)

    def contour(self, ship, verb=False):
        near = [
            (-1, -1), (-1, 0), (-1, 1),
            (0, -1), (0, 0), (0, 1),
            (1, -1), (1, 0), (1, 1)
        ]
        for d in ship.dots:
            for dx, dy in near:
                cur = Dot(d.x + dx, d.y + dy)
                if not (self.out(cur)) and cur not in self.busy:
                    if verb:
                        self.field[cur.x][cur.y] = "."
                    self.busy.append(cur)

    def __str__(self):
        res = ""
        res += "  | 1 | 2 | 3 | 4 | 5 | 6 |"  # верхняя шапка доски
        for i, row in enumerate(self.field):
            res += f"\n{i + 1} | " + " | ".join(row) + " |"  # генерация отображения доски

        if self.hid:
            res = res.replace("■", "O")
        return res

    def out(self, d):
        return not ((0 <= d.x < self.size) and (0 <= d.y < self.size))

    # стрельба по доске
    def shot(self, d):
        if self.out(d):
            raise BoardOutException()

        if d in self.busy:
            raise BoardUsedException()

        self.busy.append(d)

# проверка на попадание и вывод результата
        for ship in self.ships:
            if d in ship.dots:
                ship.lives -= 1
                self.field[d.x][d.y] = "X"
                if ship.lives == 0:
                    self.count += 1
                    self.contour(ship, verb=True)
                    print("Корабль уничтожен!")
                    return True  # дополнительный ход при уничтожении корабля
                else:
                    print("Корабль ранен!")
                    return True  # дополнительный ход при ранении корабля

        self.field[d.x][d.y] = "."
        print("Мимо!")
        return False  # переход хода оппоненту

    def begin(self):
        self.busy = []


# параметры и свойства игрока
class Player:
    def __init__(self, board, enemy):
        self.board = board
        self.enemy = enemy

    def ask(self):
        raise NotImplementedError()

    def move(self):
        while True:
            try:
                target = self.ask()
                repeat = self.enemy.shot(target)
                return repeat
            except BoardException as e:
                print(e)


# параметры отображения и расчета хода компьютера
class AI(Player):
    def ask(self):
        d = Dot(randint(0, 5), randint(0, 5))
        print(f"Ход компьютера: {d.x + 1} {d.y + 1}")
        return d


# параметры отображения и расчета хода человека
class User(Player):
    def ask(self):
        while True:
            cords = input("Ваш ход: ").split()

            # проверка на кол-во
            if len(cords) != 2:
                print(" Введите 2 координаты! ")
                continue

            x, y = cords
            
            # проверка на числа
            if not (x.isdigit()) or not (y.isdigit()):
                print(" Введите числа! ")
                continue

            x, y = int(x), int(y)

            return Dot(x - 1, y - 1)


# Запуск игры
class Game:
    def __init__(self, size=6):  # создание игрового поля
        self.size = size  # создание игровой сетки
        pl = self.random_board()  # создание готовой расстановки кораблей для игрока
        co = self.random_board()  # создание готовой расстановки кораблей для компьютера
        co.hid = True  # скрытие кораблей противника на доске

        self.ai = AI(co, pl)  # ход компьютера
        self.us = User(pl, co)  # ход игрока

    def random_board(self):  # создание случайной игровой доски
        board = None  # стартовая доска
        while board is None:
            board = self.random_place()  # создать новую доску при её отсутствии
        return board

    def random_place(self):
        lens = [3, 2, 2, 1, 1, 1, 1]  # корабли
        board = Board(size=self.size)  # размер доски, задается в class Game
        attempts = 0
        for l in lens:
            while True:
                attempts += 1
                if attempts > 2000:  # условие прерывания генерации
                    return None
                #
                ship = Ship(Dot(randint(0, self.size), randint(0, self.size)), l, randint(0, 1))
                try:
                    board.add_ship(ship)
                    break
                except BoardWrongShipException:
                    pass
        board.begin()
        return board

# Внешний интерфейс
# Стартовая информация
    def greet(self):
        print("-" * 24)
        print(" Приветсвуем вас в игре ")
        print("     [Морской бой]     ")
        print("\n формат ввода: x y ")
        print(" x - номер строки  ")
        print(" y - номер столбца ")

# прорисовка игрового поля и ходов
    def loop(self):
        num = 0
        while True:
            print()
            print("-" * 24)
            print("Доска пользователя:")
            print(self.us.board)
            print("\nДоска компьютера:")
            print(self.ai.board)
            if num % 2 == 0:
                print("-" * 24)
                print("Ходит пользователь! Ход = " + str(num+1))
                repeat = self.us.move()
            else:
                print("-" * 24)
                print("Ходит компьютер! Ход = " + str(num+1))
                repeat = self.ai.move()
            if repeat:
                num -= 1

            if self.ai.board.count == 7:
                print("-" * 24)
                print("\nПользователь выиграл!\n")
                print(self.ai.board)
                break

            if self.us.board.count == 7:
                print("-" * 24)
                print("\nКомпьютер выиграл!\n")
                print(self.us.board)
                break
            num += 1

    def start(self):
        self.greet()
        self.loop()


g = Game()  # запуск генерации игры
g.start()  # вывод стартовой информации
