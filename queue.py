#author : Battula Neelima Chowdary
#status : developed

class Queue:
    def __init__(self):
        self.items = []

    def isEmpty(self):
        return self.items == []

    def enqueue(self, item):
        self.items.insert(0,item)

    def get_queue_top(self):
        return self.items[-1]

    def get_first_four_instructions(self):
        return self.items[-1:-5]

    def dequeue(self):
        return self.items.pop()

    def size(self):
        return len(self.items)

    def read_queue(self):
        return self.items