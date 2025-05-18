def test_greeting():
    print('Hello, world!')

def test_checkout():
    print("This is checkout")

def logout():
    print("This is logout")

def test_logout():
    logout()

def test_dummy():
    assert 1+1 == 2

def my_sum(lst: list[int]) -> int:
    return sum(lst)

my_sum([1,2,3,5])
