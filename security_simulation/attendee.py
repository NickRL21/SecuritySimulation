import numpy as N
import numpy.random as rand


from security_simulation.checkpoint import Checkpoint


class Attendee(object):
    # These values are in meters per second
    LOW_WALK_SPEED = 1.25
    HIGH_WALK_SPEED = 1.51

    def __init__(self, gender, metal_percent, current_location, time_entered, has_bag=False, is_cooperative=True):
        self.gender = gender
        self.metal_percent = metal_percent
        self.current_location = current_location
        self.time_entered = time_entered
        self.back_check_complete = False
        self.has_bag = has_bag
        self.is_cooperative = is_cooperative
        self.time_step_to_enqueue = 0  # find_checkpoint updates this value
        self.time_step_to_dequeue = 0
        self.arrives_at_checkpoint = 0
        self.total_wait = 0
        self.checkpoint_target = None
        self.status = 0 # 1= bag_check, 2 = metal detector 

    def calc_distance(self, checkpoint_loc):
        """ Calculates the distance between this attendee and a checkpoint. 
            This is used by the find_checkpoint method as a factor in determining 
            which checkpoint an attendee will go to.
        """
        return N.sqrt((self.current_location[1] - checkpoint_loc[1])**2 \
                    + (self.current_location[0] - checkpoint_loc[0])**2)

    def find_checkpoint(self, checkpoints):
        """Finds a checkpoint based on proximity and checkpoint queue size 
        
        The first factor is the proximity of a checkpoint, if a checkpoint is close, line length will be checked
        if length of the line is above a certain tolerance, a further line will be checked. Attenedee will attempt to find 
        the closest checkpoint with the shortest line. If no line is short enough, the agent will use the closest line. 
           
        Variables:
            Checkpoints: List of open checkpoints in current security configuration

        Sets the time_step_to_enque and the checkpoint_target based on the checkpoint the agent decides to go to
        Returns:
            A reference to the target checkpoint that the attendee has chosen
            """
        checkpoint_line_len = N.zeros(len(checkpoints), dtype=float)
        checkpoint_distances = N.zeros(len(checkpoints), dtype=float)

        for i in range(len(checkpoints)):
            checkpoint_line_len[i] = len(checkpoints[i].check_queue)
            checkpoint_distances[i] = self.calc_distance(checkpoints[i].location)
        
        min_length = N.min(checkpoint_line_len)
        min_dist = N.min(checkpoint_distances)
        # If the min_length of all lines is > 0, divide all lengths by the min_length
        if (min_length > 0):
            checkpoint_line_len = checkpoint_line_len / min_length
        # Same idea for the distances
        if (min_dist > 0):
            checkpoint_ratios = checkpoint_distances / min_dist
        
        # Add these values together, and choose the smallest value
        checkpoint_rankings = checkpoint_ratios + checkpoint_line_len
        min_index = N.argmin(checkpoint_rankings)
        # found the target checkpoint, set that as the target_checkpoint
        self.checkpoint_target = checkpoints[min_index]
        self.calc_checkpoint_arrival(checkpoint_distances[min_index])
        return self.checkpoint_target

    def calc_checkpoint_arrival(self, distance):
        """ Calculate the time step that an attendee arrives at their target checkpoint 
            distance: the distance in meters from attendee's spawn to the checkpoint
            Generates a random speed in mps from average walking speeds"""
        # From: https://en.wikipedia.org/wiki/Walking, use random float between 4.51() kph (1.25 mps) to 5.43 kph (1.51 mps) to simulate
        # a walking speed
        attendee_speed = rand.normal(loc=1.25, scale=1.51)
        self.time_step_to_enqueue = N.ceil((distance / attendee_speed)) + self.time_entered
        return self.time_step_to_enqueue

    def calc_total_wait(self, current_time_step):
        """Calculates the total wait time (this is also the total time the attendee spent in the simulation) 
            Current_time_step is the time step at which the attendee exited the simulation (i.e. passed through security.)
            returns:
                The total wait time of the attendee in seconds"""
        self.total_wait = current_time_step - self.time_entered
        return self.total_wait

    def start_queue_time(self, time):
        """setter function used to set the start time for an attendee who recently was added to a queue 
           
        This function is called from checkpoint class. Used to store the start time for an attendee's queue experience   
        
        Variables
        time: The current time is an integer that be will be passed in as a parameter
  
            """
        self.time_step_to_enqueue = time

    def end_queue_time(self, time):
        """setter function used to set the end time for an attendee who recently was poped out of queue 
           
       This function is called from checkpoint class. It is called when attendee 
       exits the queue and has gone through security. Wait time will stop at this time 
        
        Variables
        time: The current time is an integer that be will be passed in as a parameter
  
            """
        self.time_step_to_dequeue = time

    def arrived_at_checkpoint(self, current_time):
        """Check if the current attendee should be moved to the checkpoint 
            Returns True if the current time step == this attendee's checkpoint arrival time
            Returns False if not """
        if (current_time == self.arrives_at_checkpoint):
            return True
        
        return False

    def update(self, time_step):
        """ Performs the necessary updates for this attendee may not be necessary but leaving here to come back to """
        pass
