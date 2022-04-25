import math
import random
import matplotlib.pyplot as plt
import numpy as np

num_iterations = 5


class SensorNetwork:
    """
    Can only read values from nodes, not write them (decentralized network)
    - Know if primary user is active
    - Know what Secondary Users exist, and what they believe/do
    """
    users = []  # devices in the network
    numChannels = 1  # available channels
    data = []  # row 0 = PU, row 1-n = SU; z0 = channel use, z1=belief
    clock = 0

    def __init__(self, user_list, primary_user):
        self.users = user_list
        self.primary_user = primary_user
        self.data = np.zeros(shape=(len(users) + 1, num_iterations, 2))

    def update_users(self):
        """
        Advance each Secondary User's clock one step
        :return:
        """
        signal = random.randint(0, 1)
        self.data[0, self.clock, 0] = signal

        for index, user in enumerate(self.users):
            user.update(self.primary_user_strength(user, signal), self.clock, 0)
            self.data[index, self.clock, 0] = user.get_action()
            self.data[index, self.clock, 1] = user.get_belief()

        self.clock += 1
        return signal

    def primary_user_strength(self, user, signal):
        distance = math.sqrt((user.x - self.primary_user.x) ** 2 + (user.y - self.primary_user.y) ** 2)
        noise = (random.random() - 0.5) / 2
        return signal + noise * distance ** 2


class User:
    x = 0  # x position
    y = 0  # y position
    clock = 0  # Keeps track of the logical time for a device
    id_value = 0  # This user's id for distinguishability
    channel_allocated = False  # Boolean, is a the channel allocated for this device
    primary_user_value = False  # The belief on whether or not primary user is in the channel
    user_list = []  # neighbors this device can broadcast to

    def __init__(self, id_val, x, y):
        self.id_value = id_val
        self.x = x
        self.y = y


class SecondaryUser(User):
    """
    A "good faith" SU, no malicious behavior
    """
    trust_values = []  # The perceived trust values of other users
    channel_allocated = False

    def __init__(self, id_val, x, y, neighbors):
        self.trust_values = [100] * len(neighbors)
        self.user_list = neighbors
        super().__init__(id_val, x, y)

    def set_users(self, neighbors):
        self.user_list = neighbors

    # Inspired by the following StackOverflow thread
    # https://stackoverflow.com/questions/10324015/fitness-proportionate-selection-roulette-wheel-selection-in-python
    def choose_next_broadcaster(self):
        cumulative_trust = sum([user.trust_value for user in self.user_list])
        selection_probs = [user.trust_value / cumulative_trust for user in self.user_list]
        return random.choices(self.user_list, weights=selection_probs)

    def synchronize_trust(self):
        """
        Communicate/receive trust values from other users.
        Ignore broadcast procedures, they can get values from other users at any time.
        """
        beliefs = []

        for user in self.user_list:
            # Iterate through the list of all users, get their belief
            # of if the PU is present
            # get_belief returns a bool, which we convert to an int
            beliefs.append(int(user.get_belief()))

        # if this is true then all nodes are reporting that
        # the PU is present except for 1 - the MU
        if sum(beliefs) == len(self.user_list) - 1:
            MU_index = beliefs.index(0)
            self.user_list[MU_index].trust_value = max(self.user_list[MU_index].trust_value - 10,
                                                       0)  # bound CTVs between 0 and 200

        # if this is true all users are reporting that
        # the PU is NOT present except for 1 - the MU
        elif sum(beliefs) == 1:
            MU_index = beliefs.index(1)
            self.user_list[MU_index].trust_value = max(self.user_list[MU_index].trust_value - 15,
                                                       0)  # bound CTVs between 0 and 200

        else:
            mean = self.trust_values
            # as there has been no detection of an SSDF attack by either devices
            # the nodes are rewarded by having their trust values incremented by 5
            for user in self.user_list:
                mean += user.get_trust_values()

            mean = (1 / len(self.user_list)) * mean

            self.trust_value = min(mean + 5, 200)  # bound CTV between 0 and 200

    def receive_broadcast(self, sender_id, trust_value_other_device):
        """
        Recieve a broadcast of trust values from another device and update
        the instance's trust values accordingly
        """
        # compare the nodes trust values and use that as a weight to update the trust
        # values of the device
        self.synchronize_trust(trust_value_other_device)

    def broadcast(self):
        """
        Broadcast values to all other users
        """
        # For all users in the network, make them recieve
        # the trust values of this particular instance
        for neighbor in self.user_list:
            neighbor.receive_broadcast(self.trust_values)

    def update(self, primary_user_value, clock, channel_value):
        """
        Decide what actions to take, synchronize trust? Broadcast values? Use channel?
        :return:
        """
        self.clock = clock
        self.primary_user_value = primary_user_value
        x = random.random()

        if x < 0.3334:  # take channel process
            if primary_user_value == 0 and channel_value == 0:
                # if the the id of the device matches the id of
                # the device chosen from our roulette wheel function
                # allocate it the channel
                if self.id_val == self.choose_next_broadcaster().id_val:  # highest in network
                    self.channelAllocated = True
        elif x < 0.6667:  # tri-message trust sync
            self.synchronize_trust()
        else:  # broadcast
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

    def get_trust_values(self):
        """
        :return: int the trust value
        """
        return self.trust_values


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


def generate_point(mean_x, mean_y, deviation_x, deviation_y):
    return random.gauss(mean_x, deviation_x), random.gauss(mean_y, deviation_y)


def initializeUsers():
    users = []
    # Add 1 primary User
    # Add Secondary Users to network
    cluster_mean_x = 1
    cluster_mean_y = 1
    cluster_deviation_x = 1
    cluster_deviation_y = 1
    point_deviation_x = 0.2
    point_deviation_y = 0.2

    number_of_clusters = 5
    points_per_cluster = 50

    cluster_centers = [generate_point(cluster_mean_x,
                                      cluster_mean_y,
                                      cluster_deviation_x,
                                      cluster_deviation_y)
                       for _ in range(number_of_clusters)]

    points = [generate_point(center_x,
                             center_y,
                             point_deviation_x,
                             point_deviation_y)
              for center_x, center_y in cluster_centers
              for _ in range(points_per_cluster)]

    for idx, p in enumerate(points):
        users.append(SecondaryUser(idx, p[0], p[1]))
    return users


def plot_users(users, primary_user):
    plt.scatter([user.x for user in users], [user.y for user in users])
    plt.scatter(primary_user.x, primary_user.y, c="red")
    plt.show()


if __name__ == '__main__':
    users = initializeUsers()
    net = SensorNetwork(users, SecondaryUser(-1, 1, 1))
    vals = []
    for i in range(num_iterations):
        net.update_users()
    plot_users(users, SecondaryUser(-1, 1, 1))
