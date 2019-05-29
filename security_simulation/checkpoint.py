import random as r
from security_simulation.security_agent import SecurityAgent
from security_simulation.bag_check import BagCheck
# from security_agent import SecurityAgent
# from bag_check import BagCheck


class Checkpoint(object):
    
    def __init__(self, security_roles, bag_check=None, num_metal_detectors=0, location=(0, 0), attendees_entered_event_ref=None):
        """
        initializes checkpoint object
        :param security_roles: [bag checkers, person/metal detector, person after detector]
        :param bag_check: will be setting this bag_check value later
        :num_metal_detectors: will be setting this num_metal_detectors value later
        """
        self.security_agent_list = []
        self.metal_detector_agents = []  # keep an extra ref to metal detector agents for efficiency
        self.security_roles = security_roles
        self.bag_check = bag_check
        self.num_metal_detectors = num_metal_detectors
        self.main_queue = []
        self.location = location
        self.assign_roles()
        self.attendees_entered_event = attendees_entered_event_ref
        # replace with empty list when left empty for testing
        if self.attendees_entered_event is None:
            self.attendees_entered_event = []

    # Security personnel are instantiated and are assigned roles based on input
    # index 0 refers to num of security for bag check
    # index 1 refers to num security in metal detector
    # index 2 refers num of security after detector
    def assign_roles(self):
        """
        Create security agents from security_roles array
        Security personnel are instantiated and are assigned roles based on input
        """
        for index in range(len(self.security_roles)):
            num_agents_of_type = self.security_roles[index]
            role = None
            gender = None
            agent = None
            # index 0 refers to num of security for bag check
            # index 1 refers to num security in metal detector
            # index 2 refers num of security after detector
            for i in range(num_agents_of_type):
                if r.random() < .50:
                    gender = "M"
                else:
                    gender = "F"
                if index == 0: 
                    agent = SecurityAgent(role='BAG_CHECK', gender=gender)
                elif index == 1:
                    agent = SecurityAgent(role='METAL_DETECTOR', gender=gender)
                    self.num_metal_detectors = num_agents_of_type
                    self.metal_detector_agents.append(agent)
                elif index == 2:
                    agent = SecurityAgent(role='STANDING', gender=gender)
                self.security_agent_list.append(agent)
                print("at index:", index, "=", num_agents_of_type, agent.role)
        self.bag_check = BagCheck(self.security_agent_list)
                  
    def add_attendee(self, attendee, current_sim_time):
        """
        adds an attendee to a specific checkpoint queue
        :param attendee: attendee object to add to queue
        :param current_sim_time: current time of the simulation
        :return: length of queue int
        """
        self.main_queue.append(attendee)
        attendee.start_queue_time(current_sim_time)  # the time attendee has entered queue
        return len(self.main_queue)

    def metal_detector_update_cycle(self, current_sim_time):
        for agent in self.metal_detector_agents:
            # see if agent is ready to admit attendee
            if agent.busy:
                if agent.busy_until < current_sim_time:
                    # admit attendee to event
                    attendee = agent.assigned_attendee
                    # use busy until instead of current time because it will be an exact entrance time
                    attendee.total_wait = attendee.calc_total_wait(agent.busy_until)
                    attendee.time_step_to_dequeue.end_queue_time(agent.busy_until)
                    self.attendees_entered_event.append(agent.assigned_attendee)
                    # free agent up
                    agent.busy = False
                    agent.assigned_attendee = None
            if agent.busy: # agent is still busy:
                pass
            else:
                # grab first in line but to not pop yet
                first_in_line = self.main_queue[0]
                if first_in_line.has_bag:
                    if first_in_line.bag_check_complete:
                        pass
                    else:
                        # not finished bag check so can't be metal detected
                        break
                else:

    def bag_check_update_cycle(self, current_sim_time):
        pass
    
    def update(self, current_sim_time):
        """
        update function cycles through the queue, updates status of security
        and pops attendee's that are finished waiting
        :param current_sim_time: current time of the simulation
        """
        self.bag_check_update_cycle(current_sim_time)
        self.metal_detector_update_cycle(current_sim_time)

    def average_wait_time(self):
        """
        calculates the average wait time for a specific checkpoint location
        :return: integer value that represents average wait time
        """
        time_list = self.bag_check.get_wait_time()
        time = sum(time_list) 
        time = time / len(time_list)
        
    def get_security(self):  
        """
        get method to return access to security agent list to external classes
        :return: list of security agents
        """ 
        return self.security_agent_list
        
    def get_line_length(self):  
        """
        get method to return length of main_queue which contains attendees
        """ 
        return len(self.main_queue)                                               

    def get_location(self):
        """ 
        get method to return the location at which this checkpoint exists
        """
        return self.location
