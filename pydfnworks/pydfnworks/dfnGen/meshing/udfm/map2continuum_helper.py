import numpy as np


def in_domain(self, point, buffer = 0):
    """ Checks is a point is within the domain
    
    Parameters
    ---------------
        self : DFN object
        point : numpy array
            x,y,z coordinates of point
        buffer : float
            buffer zone from the boundary. If non-zero, then it is determiend with the point is within the domain shrunk by the buffer zone

    Returns
    ----------
        bool : True if in the domain / False if not
    Notes
    ----------
        None

        
    """
    if point[0] < self.x_min + buffer: 
        return False
    elif point[0] > self.x_max - buffer:
        return False 

    elif point[1] < self.y_min + buffer: 
        return False
    elif point[1] > self.y_max - buffer: 
        return False

    elif point[2] < self.z_min + buffer: 
        return False
    elif point[2] > self.z_max - buffer: 
        return False
    else:
        return True

def gather_points(self):
    """ Gets one point from each fracture within the domain

    Parameters
    --------------
        self : DFN Object

    Returns
    --------
        points : numpy array
            Array for x,y,z points on fractures. num_frac long
    Notes
    -----------
        Attempts to grab fracture center first. If the center is outside of the domain, then we walk through the vertices until we find one that is within the domain using a buffer zone of h. The latter is to ensure don't run into any floating point issues within inside/outside the domiain. 
    
    """
    print("--> Gathering points on fractures")
    points = np.zeros((self.num_frac,3))
    for i in range(self.num_frac):
        ## first check if the fracture center is in the domain
        center = self.centers[i]
        if self.in_domain(center, self.h*10**-3):
            points[i] = center
        else:
            # if not, cycle through vertices on the fracture to find one comfortablly in the domain
            name = f'fracture-{i+1}'
            num_pts = len(self.polygons[name])
            point = self.polygons[name][0]
            j = 0
            while not self.in_domain(point, self.h*10**-3):
                j +=1 
                point = self.polygons[name][j]
                if j == num_pts:
                    print(f'--> Warning. Fracture {i+1} has a center and all vertices either outside the domain or on the boundary. Could be a problem.')
                    break
            points[i] = point

    print("--> Gathering points on fractures : Complete\n")
    return points 

            