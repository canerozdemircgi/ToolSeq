# coding=utf-8
import random

def betavariate(alpha, beta):
	return random.betavariate(alpha, beta)

def expovariate(lambd):
	return random.expovariate(lambd)

def gammavariate(alpha, beta):
	return random.gammavariate(alpha, beta)

def gauss(mu, sigma):
	return random.gauss(mu, sigma)

def lognormvariate(mu, sigma):
	return random.lognormvariate(mu, sigma)

def normalvariate(mu, sigma):
	return random.normalvariate(mu, sigma)

def paretovariate(alpha):
	return random.paretovariate(alpha)

def triangular(low, high, mode):
	return random.triangular(low, high, mode)

def uniform(low, high):
	return random.uniform(low, high)

def vonmisesvariate(mu, kappa):
	return random.vonmisesvariate(mu, kappa)

def weibullvariate(alpha, beta):
	return random.weibullvariate(alpha, beta)

def solo(val):
	return val

def custom():
	return 0