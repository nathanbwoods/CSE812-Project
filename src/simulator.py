import math
import random
import matplotlib.pyplot as plt

class SensorNetwork:
    """
    Can only read values from nodes, not write them (decentralized network)
    - Know if primary user is active
    - Know what Secondary Users exist, and what they believe/do
    """
    users = []  # devices in the network
    numChannels = 1  # available channels

    def __init__(self, userlist, primaryuser):
        self.users = userlist
        self.primaryuser = primaryuser

    def update_users(self):
        """
        Advance each Secondary User's clock one step
        :return:
        """
        signal = random.randint(0, 1)
        for user in self.users:
            user.update(self.primary_user_strength(user, signal))
        return signal

    def primary_user_strength(self, user, signal):
        distance = math.sqrt((user.x - self.primaryuser.x)**2 + (user.y - self.primaryuser.y)**2)
        noise = (random.random()-0.5)/2
        return signal + noise * distance**2


class User:
    id_value = 0  # this user's id for distinguishability
    channelAllocated = False
    timeSinceAllocation = 0  # elapsed time since this device used a channel
    x = 0 # x position
    y = 0 # y position

    def __init__(self, id_val, x, y):
        self.id_value = id_val
        self.x = x
        self.y = y


class SecondaryUser(User):
    """
    A "good faith" SU, no malicious behavior
    """
    trustValue = 0  # user's evaluation of its own trustworthiness
    users = []  # other users that this device is knows of
    trustValues = []  # perceived trust values of other users

    def synchronizeTrust(self):
        """
        Communicate/receive trust values from other users.
        Ignore broadcast procedures, they can get values from other users at any time.
        :return:
        """
        i = 0
        for user in self.users:
            # compare two trust values
            dif = self.users[i].trustValue - self.trustValues[i]
            i += 1

    def update(self, signal):
        """
        Decide what actions to take, synchronize trust? Broadcast values?
        :return:
        """
        pass


class MaliciousUser(SecondaryUser):
    """
    Users with potential to be malicious, some strategy
    """
    pass


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

    for i, p in enumerate(points):
        users.append(SecondaryUser(i, p[0], p[1]))
    return users


def plot_users(users, primary_user):
    plt.scatter([user.x for user in users], [user.y for user in users])
    plt.scatter(primary_user.x, primary_user.y, c="red")
    plt.show()


if __name__ == '__main__':
    users = initializeUsers()
    net = SensorNetwork(users, SecondaryUser(-1, 1, 1))
    vals = []
    for i in range(5000):
        net.update_users()
    plot_users(users, SecondaryUser(-1, 1, 1))
