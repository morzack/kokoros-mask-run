from pygame.event import EventType
from pygame import Surface

class State:
    """
    implements basic state machine logic
    """
    
    def __init__(self):
        self.start_time = 0.0
        self.current_time = 0.0
        
        self.running = False

        self.next_state = None
        self.previous_state = None

    def process_event(self, event : EventType):
        """
        process a pygame event, to be overridden
        """
        pass
    
    def start(self, current_time):
        """
        start the state
        """
        self.running = True
        self.start_time = current_time

    def update(self, surface : Surface, keys_pressed, current_time):
        """
        update the state and draw, to be overridden
        """
        pass