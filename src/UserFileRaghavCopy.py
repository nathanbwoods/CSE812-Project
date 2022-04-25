import random

class User:
    clock = 0 # Keeps track of the logical time for a device
    id_value = 0 # This user's id for distinguishability
    channelAllocated = False # Boolean, is a the channel allocated for this device
    timeSinceAllocation = 0 # The elapsed time since this device used a channel 
    num_users = 0 # The total number of users in our network
    #user_ids = [] # List containing all instances (ids) of Users in our network
    user_list = []

    def __init__(self, id_val):
        self.id_value = id_val

        User.num_users += 1 # Update the number of users everytime a new user is created 
        #User.user_ids.append(self.id) # Append the new user id to a list shared between all user instances
        User.user_list.append(self)

class SecondaryUser(User):
    """
    A "good faith" SU, no malicious behavior
    """
    trust_value = 0 # The user's evaluation of its own trustworthiness, scaled -100 to 100
    all_trust_values = [0*(len(User.user_list))] # The perceived trust values of other users
    primary_user_value = False # The belief on whether or not primary user is in the channel
    
    def set_users(self, users):
        self.user_list = User.user_list
    
    def synchronize_trust(self):
        """
        Communicate/receive trust values from other users.
        Ignore broadcast procedures, they can get values from other users at any time.
        :return:
        """
        for i in range(len(self.user_list)):
            # Iterate through the list of all users, get their trust value
            # and compare it to the trust value we have recorded on our instance 
            
            # diff = self.user_list[i].get_trust_values() - self.all_trust_values[i]
            
            # if an SSDF is detected we take punitive measure and decrement the 
            # other device's trust value by a   
            
            # Need to detect SSDF attack and decrement device's trust value

            # as there has been no detection of an SSDF attack by either devices 
            # the nodes are rewarded by having their trust values incremented by 5
            mean = (self.user_list[i].get_trust_values() + self.all_trust_values)//2
            self.user_list[i].trust_value = mean + 5
            self.trust_value = mean +  5 

    def receive_broadcast(self, trustValues):
        """
        Recieve a broadcast of trust values from another device and update 
        the instance's trust values accordingly
        """
        self.all_trust_values = trustValues
    
    def broadcast(self):
        """
        Broadcast values to all other users
        """
        # For all users in the network, make them recieve 
        # the trust values of this particular instance
        for i in range(len(self.user_list)):
            self.user_list[i].recieve_broadcast(self.all_trust_values)

    
    def update(self, primary_user_value, clock, channel_value):
        """
        Decide what actions to take, synchronize trust? Broadcast values? Use channel?
        :return:
        """
        self.clock = clock
        self.primary_user_value = primary_user_value
        x = random.random()
        
        if x < 0.3334: #take channel process
            if primary_user_value == 0 and channel_value == 0:
                if self.trust_value == 100:
                    self.channelAllocated = True
        elif x < 0.6667: # tri-message trust sync
            self.synchronize_trust()
        else: # broadcast
            self.broadcast()
                    
        def get_action(self):
            """:
            return: boolean true if channel is allocated to this SU 
            """
            return self.channel_allocated
    
        def get_belief(self):
            """
            :return: boolean true if channel is believed to be allocated to PU
            """
            return User.primary_user_value
    
        def get_trust_value(self):
            """
            :return: int the trust value
            """
            return self.trust_value
    
class MaliciousUser(SecondaryUser):
    """
    Users with potential to be malicious, some strategy:
    -Selfish SSDF: Falsely report that PU is present, in order to gain exclusive access to the desired
    spectrum.
    - Interference SSDF: Falsely report that PU is not present, in order to cause interference to PU.
    - Confusing SSDF: Randomly reports a true or false value for primary user energy, preventing a
    consensus.
    """
    
    def SelfishSSDF(self):
        if not self.get_belief():
            self.primary_user_value = True 

    def InterferenceSSDF(self):
        if self.get_belief():
            self.primary_user_value = False
    
    def ConfusingSSDF(self):
        z = random.random()
        if z < 0.5:
            self.primary_user_value = True 
        else:
            self.primary_user_value = False