import networkx as nx
import numpy as np
import numpy.random 
import sys

# pydfnworks modules
import pydfnworks.dfnGraph.graph_flow 

def create_neighbour_list(Gtilde):
    """ Create a list of downstream neighbour vertices for every vertex on NetworkX graph obtained after running graph_flow

    Parameters
    ----------
        Gtilde: NetworkX graph 
            obtained from output of graph_flow

    Returns
    -------
        dict : nested dictionary.

    Notes
    -----
    dict[n]['child'] is a list of vertices downstream to vertex n
    dict[n]['prob'] is a list of probabilities for choosing a downstream node for vertex n
    """

    nbrs_dict = {}

    for i in nx.nodes(Gtilde):

        if Gtilde.nodes[i]['outletflag']:
            continue
        
        node_list =  []
        prob_list = []
        nbrs =  nx.neighbors(Gtilde, i)
        nbrs_dict[i] = {}
        
        for v in nx.neighbors(Gtilde, i):
            delta_p = Gtilde.nodes[i]['pressure'] - Gtilde.nodes[v]['pressure'] 

            if  delta_p > np.spacing(Gtilde.nodes[i]['pressure']):
                node_list.append(v)
                prob_list.append(Gtilde.edges[i, v]['flux'])
        
        if node_list:
            nbrs_dict[i]['child'] = node_list
            nbrs_dict[i]['prob'] = np.array(prob_list, dtype=float)/sum(prob_list)
        else:
            nbrs_dict[i]['child'] = None
            nbrs_dict[i]['prob'] = None
    
    return nbrs_dict 



class Particle():
    ''' 
    Class for graph particle tracking, instantiated for each particle


    Attributes:
        * time : Total time of travel of particle [s]
        * dist : total distance traveled [m]
        * flag : True if particle exited system, else False
        * frac_seq : Dictionary, contains information about fractures through which the particle went
    '''


    def __init__(self):
        self.frac_seq = {}
        self.time = float
        self.dist = float
        self.flag = bool

    def set_start_time_dist(self, t, L):
        """ Set initial value for travel time and distance

        Parameters
        ----------
            self: object
            t : double
                time in seconds
            L : double
                distance in metres

        Returns
        -------

        """

        self.time = t
        self.dist = L
    
    def track(self, Gtilde, nbrs_dict):
        """ track a particle from inlet vertex to outlet vertex

        Parameters
        ----------
            Gtilde : NetworkX graph
                graph obtained from graph_flow

            nbrs_dict: nested dictionary
                dictionary of downstream neighbours for each vertex

        Returns
        -------

        """

        Inlet = [v for v in nx.nodes(Gtilde) if Gtilde.nodes[v]['inletflag']]
        curr_v = numpy.random.choice(Inlet)
        while True:
            if Gtilde.nodes[curr_v]['outletflag']:
                self.flag = True
                break
            if nbrs_dict[curr_v]['child'] is None:
                print("Warning!!! No child found")
                self.flag = False
                break
            next_v =  numpy.random.choice(nbrs_dict[curr_v]['child'], p=nbrs_dict[curr_v]['prob'])

            frac = Gtilde.edges[curr_v, next_v]['frac']
            t = Gtilde.edges[curr_v, next_v]['time']
            L  = Gtilde.edges[curr_v, next_v]['length']
            self.add_frac_data(frac, t, L)
            curr_v = next_v

    
    def add_frac_data(self, frac, t, L):
        """ add details of fracture through which particle traversed

        Parameters
        ----------
            self: object

            frac: int
                index of fracture in graph

            t : double
                time in seconds

            L : double
                distance in metres

        Returns
        -------

        """

        self.frac_seq.update({frac : {'time':0.0, 'dist':0.0}})
        self.frac_seq[frac]['time'] += t
        self.frac_seq[frac]['dist'] += L 
        self.time += t
        self.dist += L

    
    
    def write_file(self, partime_file=None, frac_id_file=None):
        """ write particle data to output files, if supplied

        Parameters
        ----------
            self: object

            partime_file : string
                name of file to  which the total travel times and lengths will be written for each particle, default is None

            frac_id_file : string
                name of file to which detailed information of each particle's travel will be written, default is None
        
        Returns
        -------
        """

        if partime_file is not None:
            with open(partime_file, "a") as f1:
                f1.write("{:3.3E}  {:3.3E} \n".format(self.time, self.dist))
        
        if frac_id_file is not None:
            data1 =  []
            data1 = [key for key in self.frac_seq if isinstance(key, dict) is False]
            n = len(data1)
            with open(frac_id_file, "a") as f2:
                for i in range(3*n):
                    if i < n:    
                        f2.write("{:d}  ".format(data1[i]))
                    elif n-1 < i < 2*n:
                        f2.write("{:3.2E}  ".format(self.frac_seq[data1[i-n]]['time']))
                    else:
                        f2.write("{:3.2E}  ".format(self.frac_seq[data1[i-2*n]]['dist']))
                f2.write("\n")






def run_graph_transport(self, Gtilde, nparticles, partime_file=None, frac_id_file=None):
    """ Run  particle tracking on the given NetworkX graph

    Parameters
    ----------
        self : object
            DFN Class
            
        Gtilde : NetworkX graph 
            obtained from graph_flow

        nparticles: int 
            number of particles

        partime_file : string
            name of file to  which the total travel times and lengths will be written for each particle, default is None

        frac_id_file : string
            name of file to which detailed information of each particle's travel will be written, default is None

    Returns
    -------

    Notes
    -----
    Information on individual functions is found therein
    """
    
    
    if partime_file is not None:
        try:
            with open(partime_file, "w") as f1:
                f1.write("# exit time (s)  total distance covered (m)\n")
        except:
            error="ERROR: Unable to open supplied partime_file file {}".format(partime_file)
            sys.stderr.write(error)
            sys.exit(1)

    if frac_id_file is not None:        
        try:
            with open(frac_id_file, "w") as f2:
                f2.write("# Line has (n+n+n) entries, consisting of all frac_ids (from 0), times spent (s), dist covered (m)\n")
        except:
            error="ERROR: Unable to open supplied frac_id_file file {}".format(frac_id_file)
            sys.stderr.write(error)
            sys.exit(1) 

    nbrs_dict = create_neighbour_list(Gtilde)
    print("Creating downstream neighbour list")
    Inlet = [v for v in nx.nodes(Gtilde) if Gtilde.nodes[v]['inletflag']]
    
    pfailcount = 0
    print("Starting particle tracking")

    for i in range(nparticles):
        print(i)
        particle_i = Particle()
        particle_i.set_start_time_dist(0, 0)
        particle_i.track(Gtilde, nbrs_dict)

        if particle_i.flag:
            particle_i.write_file(partime_file, frac_id_file)
        else:
            pfailcount += 1

    print("Particle tracking complete")
    if pfailcount == 0:
        print("All particles exited")
    else:
        print("Out of {} particles, {} particles did not exit".format(nparticles, pfailcount))
    return
