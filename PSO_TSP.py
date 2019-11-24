from operator import attrgetter
import random, copy

class Graph:
    def __init__(self, amount_vertices): # (self, int)
        self.edges = {} # dict of edges
        self.vertices = set() # set of vertices
        self.amount_vertices = amount_vertices # amount of vertices

    # tambahin edge dari "source" ke "destination" beserta "cost" nya
    def addEdge(self, source, destination, cost=0):
        # buat edge hanya jika edge belum ada
        if not self.isEdgeExist(source, destination):
            self.edges[(source, destination)] = cost
            self.vertices.add(source)
            self.vertices.add(destination)

    def isEdgeExist(self, source, destination):
        return True if (source, destination) in self.edges else False

    # return total cost suatu path (path = list of vertex)
    def getCostPath(self, path):
        total_cost = 0
        for i in range(self.amount_vertices - 1):
            total_cost += self.edges[(path[i], path[i+1])]

        # add cost edge terakhir (vertex terakhir ke vertex asal)
        total_cost += self.edges[(path[self.amount_vertices - 1], path[0])]
        return total_cost

    def getVertices(self):
        return list(self.vertices)

    # get random unique path - return list of lists of paths
    def getRandomPaths(self, max_size, initial_vertice=-1):
        random_paths = []
        list_vertices = list(self.vertices)

        if initial_vertice == -1:
            initial_vertice = random.choice(list_vertices) # ambil vertex secara acak

        # pindahkan vertex awal ke index 0
        list_vertices.remove(initial_vertice)
        list_vertices.insert(0, initial_vertice)

        for i in range(max_size):
            while True:
                list_temp = list_vertices[1:] # path index 1 - terakhir
                random.shuffle(list_temp) # shuffle vertex
                list_temp.insert(0, initial_vertice) # masukkan vertex awal ke index 0 path nya

                # pastikan ga ada duplikat path yang terbentuk
                if list_temp not in random_paths:
                    random_paths.append(list_temp)
                    break # break the while True loop

        return random_paths


class Particle:
    def __init__(self, solution, cost): # (self, path/list of vertices(list of int), int)
        self.solution = solution # current solution
        self.pbest = solution # best solution (fitness) yang sudah dicapai sejauh ini
        self.cost_current_solution = cost # cost current solution
        self.cost_pbest_solution = cost # cost pbest solution

        # velocity particle = deretan dari 4 tuple
        # contoh: (1, 2, "beta") artinya solution(1, 2), probability "beta"
        self.velocity = []

    # setters and getters
    def setPBest(self, new_pbest):
        self.pbest = new_pbest

    def getPBest(self):
        return self.pbest

    def setVelocity(self, new_velocity): # (sequence of swap operators)
        self.velocity = new_velocity

    def getVelocity(self):
        return self.velocity

    def setCurrentSolution(self, solution):
        self.solution = solution

    def getCurrentSolution(self):
        return self.solution

    def setCostPBest(self, cost):
        self.cost_pbest_solution = cost

    def getCostPBest(self):
        return self.cost_pbest_solution

    def setCostCurrentSolution(self, cost):
        self.cost_current_solution = cost

    def getCostCurrentSolution(self):
        return self.cost_current_solution

    # remove semua element di list velocity
    def clearVelocity(self):
        del self.velocity[:]


# PSO Algorithm
class PSO:
    def __init__(self, graph, iterations, size_population, alfa=1, beta=1, initial_vertice=-1): # (self, Graph, int, int, float 0-1, float 0-1, int)
        self.graph = graph # the graph
        self.iterations = iterations # max of iterations
        self.size_population = size_population # size population
        self.particles = [] # list of particles
        self.alfa = alfa # probability that all swap operators in swap sequence (pbest - x(t-1))
        self.beta = beta # probability that all swap operators in swap sequence (gbest - x(t-1))

        # initialized with a group of random particles (solutions)
        solutions = self.graph.getRandomPaths(self.size_population, initial_vertice)

        # creates the particles and initialization of swap sequences in all the particles
        for solution in solutions:
            # create a new particle
            particle = Particle(solution=solution, cost=graph.getCostPath(solution))
            # add the particle
            self.particles.append(particle)

        # updates "size_population"
        self.size_population = len(self.particles)

    def setGBest(self, new_gbest):
        self.gbest = new_gbest

    def getGBest(self):
        return self.gbest

    # print particles information
    def showParticles(self):
        print("Particles:\n")
        for particle in self.particles:
            print(
                "pbest: %s \t|\t cost pbest: %d \t|\t current solution: %s \t|\t cost current solution: %d \n" \
                % (str(particle.getPBest()), particle.getCostPBest(), str(particle.getCurrentSolution()), particle.getCostCurrentSolution())
            )

    def run(self):
        # for each time step (iteration)
        for t in range(self.iterations):
            # updates gbest (best particle of the population)
            self.gbest = min(self.particles, key=attrgetter("cost_pbest_solution")) # ambil nilai terkecil cost_pbest_solution dari particles, return particle

            # for each particle in the swarm
            for particle in self.particles:
                particle.clearVelocity() # hapus velocity particle dulu
                temp_velocity = []
                solution_gbest = copy.copy(self.gbest.getPBest()) # gets solution of the gbest
                solution_pbest = particle.getPBest()[:] # copy of the pbest solution
                solution_particle = particle.getCurrentSolution()[:] # copy of the current solution of the particle

                # generates all swap operators to calculate (pbest - x(t-1))
                for i in range(self.graph.amount_vertices):
                    if solution_particle[i] != solution_pbest[i]:
                        # generates swap operator
                        swap_operator = (i, solution_pbest.index(solution_particle[i]), self.alfa)

                        # append swap operator in the list of velocity
                        temp_velocity.append(swap_operator)

                        # makes the swap
                        temp = solution_pbest[swap_operator[0]]
                        solution_pbest[swap_operator[0]] = solution_pbest[swap_operator[1]]
                        solution_pbest[swap_operator[1]] = temp

                # generates all swap operators to calculate (gbest - x(t-1))
                for i in range(self.graph.amount_vertices):
                    if solution_particle[1] != solution_gbest[i]:
                        # generates swap operator
                        swap_operator = (i, solution_gbest.index(solution_particle[i]), self.beta)

                        # append swap operator in the list of velocity
                        temp_velocity.append(swap_operator)

                        # makes the swap
                        temp = solution_gbest[swap_operator[0]]
                        solution_gbest[swap_operator[0]] = solution_gbest[swap_operator[1]]
                        solution_gbest[swap_operator[1]] = temp

                # updates velocity
                particle.setVelocity(temp_velocity)

                # generates new solution for particle
                for swap_operator in temp_velocity:
                    if random.random() <= swap_operator[2]: # (random.random() generate a random number [0.0, 1.0))
                        # makes the swap
                        temp = solution_particle[swap_operator[0]]
                        solution_particle[swap_operator[0]] = solution_particle[swap_operator[1]]
                        solution_particle[swap_operator[1]] = temp

                particle.setCurrentSolution(solution_particle) # updates the current solution
                cost_current_solution = self.graph.getCostPath(solution_particle)
                particle.setCostCurrentSolution(cost_current_solution) # updates the cost of the current solution

                # check if current solution is pbest solution
                if cost_current_solution < particle.getCostPBest():
                    particle.setPBest(solution_particle)
                    particle.setCostPBest(cost_current_solution)


if __name__ == "__main__":

    # manual input
    amount_vertices = int(input("amount of vertices: "))
    graph = Graph(amount_vertices=amount_vertices)
    n = int(amount_vertices*(amount_vertices-1)/2)
    print("Masukkan edges (source destination cost) sebanyak {n} kali:".format(n=n))
    for i in range(n):
        while True:
            src, dest, cost = [int(x) for x in input().split()]
            if not graph.isEdgeExist(src, dest):
                graph.addEdge(src, dest, cost)
                graph.addEdge(dest, src, cost)
                break
            print("Edge sudah ada! masukkan edge yang lain.\n")

    initial_vertice = int(input("Masukkan vertex awal: "))
    while True:
        if initial_vertice in graph.getVertices():
            break
        print("Vertex tidak ada! input ulang.")
        initial_vertice = int(input("Masukkan vertex awal: "))

    iterations = int(input("Masukkan maximum iterasi: "))
    size_population = int(input("Masukkan size populasi: "))
    alfa = float(input("Masukkan probabilitas swap operator for PBest: "))
    beta = float(input("Masukkan probabilitas swap operator for GBest: "))

    pso = PSO(graph, iterations=iterations, size_population=size_population, alfa=alfa, beta=beta, initial_vertice=initial_vertice)
    """
    # automatically input
    graph = Graph(amount_vertices=5)

    graph.addEdge(0, 1, 1)
    graph.addEdge(1, 0, 1)
    graph.addEdge(0, 2, 3)
    graph.addEdge(2, 0, 3)
    graph.addEdge(0, 3, 4)
    graph.addEdge(3, 0, 4)
    graph.addEdge(0, 4, 5)
    graph.addEdge(4, 0, 5)
    graph.addEdge(1, 2, 1)
    graph.addEdge(2, 1, 1)
    graph.addEdge(1, 3, 4)
    graph.addEdge(3, 1, 4)
    graph.addEdge(1, 4, 8)
    graph.addEdge(4, 1, 8)
    graph.addEdge(2, 3, 5)
    graph.addEdge(3, 2, 5)
    graph.addEdge(2, 4, 1)
    graph.addEdge(4, 2, 1)
    graph.addEdge(3, 4, 2)
    graph.addEdge(4, 3, 2)

    pso = PSO(graph, iterations=100, size_population=10, alfa=0.9, beta=1)
    """
    pso.run()
    pso.showParticles()

    # shows the global best particle
    print('gbest: %s | cost: %d\n' % (pso.getGBest().getPBest(), pso.getGBest().getCostPBest()))
