import copy
import sys
import time
runTime = time.time() + 179

def clausesConsistent(clauses, sol):
	for clause in clauses:
		sat = False
		for lit in clause:
			if sol[lit[0]-1][lit[1]-1] == lit[2]:
				sat = True
		if sat == False:
			return False
	return True

def clausesInconsistent(clauses, sol):
	for clause in clauses:
		empty = True
		for lit in clause:
			if (sol[lit[0] - 1][lit[1] - 1] == (not lit[2]) and (not None)) == False:
				empty = False
		if empty:
			return True
	return False

def getUnitClause(clauses, sol):
	for clause in clauses:
		sat = False
		for lit in clause:
			if sol[lit[0] - 1][lit[1] - 1] == lit[2]:
				sat = True
		if sat == False:
			leftLit = 0
			unassignedLit = None
			for lit in clause:
				if (sol[lit[0] - 1][lit[1] - 1] == (not lit[2]) and (not None)) == False:
					leftLit += 1
					unassignedLit = lit
			if leftLit == 1:
				return ((unassignedLit[0], unassignedLit[1]), unassignedLit[2])
	return (None, None)

def getPureLiteral(clauses, sol):
	trueVariables = set()
	falseVariables = set()
	for clause in clauses:
		sat = False
		for lit in clause:
			if sol[lit[0] - 1][lit[1] - 1] == lit[2]:
				sat = True
		if sat == False:
			for lit in clause:
				if sol[lit[0] - 1][lit[1] - 1] == None:
					if lit[2] is False:
						falseVariables.add((lit[0], lit[1]))
					else:
						trueVariables.add((lit[0], lit[1]))
	for v in trueVariables:
		if v not in falseVariables:
			return (v, True)
	for v in falseVariables:
		if v not in trueVariables:
			return (v, False)
	return (None, None)

def DPLL(clauses, variables, sol):
	if time.time() >= runTime:
		return (False, sol)
	if(clausesConsistent(clauses, sol)):
		return (True, sol)
	if(clausesInconsistent(clauses, sol)):
		return (False, sol)
	# Try to find a unit clause
	(variable, val) = getUnitClause(clauses, sol)
	if variable != None:
		sol[variable[0] - 1][variable[1] - 1] = val
		variables.remove(variable)
		return DPLL(clauses, variables, sol)
	# Try to find a pure literal
	(variable, val) = getPureLiteral(clauses, sol)
	if variable != None:
		sol[variable[0] - 1][variable[1] - 1] = val
		variables.remove(variable)
		return DPLL(clauses, variables, sol)
	curSol = copy.deepcopy(sol)
	curVariables = copy.deepcopy(variables)
	variable = curVariables.pop(0)
	# try to set next be True
	curSol[variable[0] - 1][variable[1] - 1] = True
	(findSol, solution) = DPLL(clauses, curVariables, curSol)
	if findSol:
		return (True, solution)
	else:
		# try to set next be False
		curSol[variable[0] - 1][variable[1] - 1] = False
		(findSol, solution) = DPLL(clauses, curVariables, curSol)
		if findSol:
			return (True, solution)
		else:
			return (False, sol)

def main():
	f = open("input.txt", "r")
	content = f.read().splitlines()
	f.close()
	numGroups = int(content[0])
	numPots = int(content[1])
	potList = []
	for i in range(2,2+numPots):
		potList.append(content[i].split(","))
	potSymList = []
	team = 1
	for i in range(0,len(potList)):
		tmp = []
		for j in range(0,len(potList[i])):
			tmp.append(team)
			team += 1
		potSymList.append(tmp)
	continentList = []
	for i in range(6):
		continentList.append(i)
	for i in range(2+numPots,len(content)):
		confederations,team = content[i].split(":")
		if confederations == "AFC":
			continentList[0] = team.split(",")
		elif confederations == "CAF":
			continentList[1] = team.split(",")
		elif confederations == "CONCACAF":
			continentList[2] = team.split(",")
		elif confederations == "CONMEBOL":
			continentList[3] = team.split(",")
		elif confederations == "OFC":
			continentList[4] = team.split(",")
		elif confederations == "UEFA":
			continentList[5] = team.split(",")
	continentSymList = []
	for i in range(6):
		tmp = []
		for j in range(0,len(continentList[i])):
			for x in range(numPots):
				for y in range(0,len(potList[x])):
					if continentList[i][j] == potList[x][y]:
						tmp.append(potSymList[x][y])
		continentSymList.append(tmp)
	# Get number of teams
	numTeams = 0
	for i in range(6):
		if continentList[i][0] != 'None':
			numTeams = numTeams + len(continentList[i])
	# Set the max recursion limit
	limit = numTeams*numGroups + 100
	sys.setrecursionlimit(limit)
	# Create an empty solution
	solution = []
	for i in range(numTeams):
		tmp = []
		for j in range(numGroups):
			tmp.append(None)
		solution.append(tmp)
	# Create variables for each combination of team and group
	variables = []
	for i in range(1,numTeams+1):
		for j in range(1,numGroups+1):
			variables.append((i,j))
	# Create CNF clauses
	clauses = []
	# Every team must be assigned to a group.
	for team in range(1, numTeams+1):
		tmp = []
		for group in range(1,numGroups+1):
			tmp.append((team, group, True))
		clauses.append(tmp)
	# Each team can not be assigned to multiple group.
	for team in range(1, numTeams+1):
		for g1 in range(1, numGroups+1):
			for g2 in range(g1+1, numGroups+1):
				clauses.append([(team, g1, False), (team, g2, False)])	
	# C1: No group can have more than one team from any pot.
	# Make sure each team in the same pot do not assigned to the same group.
	for i in range(0, numPots):
		for x in range(0,len(potSymList[i])):
			for y in range(x+1,len(potSymList[i])):
				t1 = potSymList[i][x]
				t2 = potSymList[i][y]
				for group in range(1, numGroups+1):
					clauses.append([(t1, group, False), (t2, group, False)])
	# C2: No group can have more than one team from any continental confederation, 
	# 	  with the exception of UEFA, which can have up to two teams in a group.
	# Make sure each team in the same confederation do not assigned to the same group, except UEFA.
	for i in range(0, 5):
		for x in range(0,len(continentSymList[i])):
			for y in range(x+1,len(continentSymList[i])):
				t1 = continentSymList[i][x]
				t2 = continentSymList[i][y]
				for group in range(1, numGroups+1):
					clauses.append([(t1, group, False), (t2, group, False)])
	# Make sure each team in UEFA do not assigned up to two team in a group.
	for x in range(0,len(continentSymList[5])):
		for y in range(x+1,len(continentSymList[5])):
			for z in range(y+1,len(continentSymList[5])):
				t1 = continentSymList[5][x]
				t2 = continentSymList[5][y]
				t3 = continentSymList[5][z]
				for group in range(1, numGroups+1):
					clauses.append([(t1, group, False), (t2, group, False), (t3, group, False)])
	# Run DPLL Algorithm
	(findSolution, finalSolution) = DPLL(clauses, variables, solution)
	for j in range(1,numTeams+1):
		for i in range(1,numGroups):
			variables.remove((j,i))
			variables.append((j,i))
			if findSolution == False:
				(findSolution, finalSolution) = DPLL(clauses, variables, solution)
	ans = []
	for i in range(numGroups):
		ans.append([])
	f = open("output.txt", "w")
	if findSolution:
		f.write("Yes")
		for team in range(0, numTeams):
			for group in range(0, numGroups):
				if finalSolution[team][group] is True:
					ans[group].append(team+1)
		for g in ans:
			if len(g) == 0:
				f.write("\n" + "None")
			else:
				tmp = ""
				for i in range(numPots):
					for j in range(len(potList[i])):
						if g[0] == potSymList[i][j]:
							tmp = tmp + potList[i][j]
				for t in range(1,len(g)):
					for i in range(numPots):
						for j in range(len(potList[i])):
							if g[t] == potSymList[i][j]:
								tmp = tmp + "," + potList[i][j]
				f.write("\n" + tmp)
	else:
		f.write("No")
	f.close()

main()