import numpy as np
import random
from operator import itemgetter


# Person has an id, risk aversion, value of the insured item and c for probability transform
class Person:
    def __init__(self, id, risk_aversion=1.0, loss_hate=2.0, wealth=0.0, a=1, b=0, c=0.5,
                 utility_family='power', weighting_family='linear'):
        self.id = id
        self.wealth = wealth  # Wealth of the person
        self.utility = Utility(utility_family, risk_aversion, loss_hate)
        check_params(a, b, c)
        self.weighting = Weighting(weighting_family, a, b, c)

    def set_id(self, id):
        self.id = id

    def get_id(self):
        return self.id

    # Adjusting the utility function.
    def adjust_t(self, multiplier=0.0001):
        risk_aversion = self.utility.t
        risk_aversion *= (1 + multiplier)
        self.utility.t = min([1.8, risk_aversion])  # Hard cap for rational parameters
        self.utility.t = max([0.2, risk_aversion])


class Utility:
    def __init__(self, family, t, lamb):
        self.family = family  # Utility family is one of (exponential and power)
        self.t = t  # The parameter of the utility family, determined by risk aversion
        self.lamb = lamb  # Loss hate parameter

    def set_family(self, family):
        self.family = family

    def get_family(self):
        return self.family

    def set_t(self, t):
        self.t = t

    def get_t(self):
        return self.t

    def set_lamb(self, lamb):
        self.lamb = lamb

    def get_lamb(self):
        return self.lamb

    def U(self, alpha):
        # If the value is negative, then U(a) = -lambda * U(-a)
        val = alpha
        multiplier = 1
        if alpha < 0:
            multiplier = -self.lamb
            val = -alpha
        # Power utility family
        if self.family == 'power':
            if self.t != 0:
                return np.power(val, self.t) * multiplier
            else:
                return np.log(1 + val) * multiplier

        # Exponential utility family
        else:
            if self.t != 0:
                return (1 - np.exp(-self.t * val)) * multiplier
            else:
                return alpha * multiplier

    # Certainty equivalent of a value.
    def CE(self, utility):
        # If the value is negative, then U(a) = -lambda * U(-a)
        multiplier = 1
        if utility < 0:
            multiplier = -self.lamb
        # Power utility family
        if self.family == 'power':
            if self.t != 0:
                return np.power(utility * multiplier, 1 / self.t) * multiplier
            else:
                return np.exp(utility / multiplier) - 1

        # Exponential utility family
        else:
            if self.t != 0:
                return -np.log(1 - utility / multiplier) / self.t
            else:
                return utility * multiplier


class Weighting:
    def __init__(self, family, a, b, c):
        self.family = family  # Weighting family is one of ('linear', 'S1', 'S2', 'exponential', 'power')
        # Parameters for weighting function.
        self.a = a
        self.b = b
        self.c = c

        if family not in ['linear', 'S1', 'S2', 'exponential', 'power'] or type(family) != str:
            raise ValueError('Weighting family must be 1 of: (linear, S1, S2, exponential, power)')

        if family == 'linear':
            if a + b > 1:
                raise ValueError('a + b must be lower than 1')

            if a < 0 or b < 0:
                raise ValueError('a and b must be greater than 0')

        if family == 'S1':
            if c < 0.28:
                raise ValueError('c must be greater than 0.28')

    def set_family(self, family):
        self.family = family

    def get_family(self):
        return self.family

    def set_params(self, a, b, c):
        check_params(a, b, c)
        self.a = a
        self.b = b
        self.c = c

    def W(self, probability):
        # S - shape weighting family with 1 parameter
        if self.family == 'S1':
            top = np.power(probability, self.c)
            bottom = np.power(top + np.power(1 - probability, self.c), 1 / self.c)
            return top / bottom

        # S - shape weighting family with 2 parameters
        elif self.family == 'S2':
            top = np.power(probability, self.b)
            bottom = self.b * np.power(probability, self.a) + np.power(1 - probability, self.a)
            return top / bottom

        # Linear weighting family
        elif self.family == 'linear':
            if probability == 1:
                return 1
            return self.b + self.a * probability

        # Exponential weighting family
        elif self.family == 'exponential':
            return np.exp(-self.b * (np.power(-np.log(probability), self.a)))

        # Power weighting family
        elif self.family == 'power':
            return np.power(probability, self.c)


def check_params(a, b, c):
    if type(a) == str or type(b) == str or type(c) == str:
        print(type(a), type(b), type(c))
        raise ValueError('a, b and c must be of type float')


# Each node has links to other nodes, when each link has probability or not, if it's a choice.
def prospect(person, node):
    outcomes = []
    # Organising the outcomes
    for l in node.links:
        outcomes.append((l.probability, l.node_in))

    # Getting the utilities of the outcomes
    for outcome in outcomes:
        outcome[1].calc_utility(person)

    # Sorting the outcomes for the model
    outcomes_sorted = sorted(outcomes, key=itemgetter(1), reverse=True)
    cum_p = 0
    V = 0
    w_prev = 0
    # Calculating the utility of the node based on Prospects Theory.
    for outcome in outcomes_sorted:
        probability = outcome[0]
        u = outcome[1].utility
        cum_p += probability
        V += (person.weighting.W(cum_p) - w_prev) * u
        w_prev = person.weighting.W(cum_p)
    return V


# Generating population.
def generate_population(n_people, min_t=0.5, max_t=1.3, min_c=0.28, max_c=1.5, value=70000):
    people = {}
    for i in range(n_people):
        loss_hate = random.uniform(1, 3)
        t = random.uniform(min_t, max_t)
        wealth = random.uniform(6, 10) * value
        c = random.uniform(min_c, max_c)
        people[i] = Person(i, t, loss_hate, wealth, 1, 1, c, 'power', 'S1')
    return people



