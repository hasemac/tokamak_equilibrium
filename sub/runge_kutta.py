class Runge_kutta:
    """Solve differential equation with 4-th Runge Kutta
    The function given in initialization must be a class,
    and have the following methods.
    
    fnc.get_val(t0, x0)
    fnc.is_end(t0, x0)
    
    """
    def __init__(self, func):
        self.fnc = func
        
    def one_step(self, t0, x0, dt):
        fnc = self.fnc

        k1 = dt * fnc.get_val(t0, x0)
        k2 = dt * fnc.get_val(t0+dt/2, x0+k1/2)
        k3 = dt * fnc.get_val(t0+dt/2, x0+k2/2)
        k4 = dt * fnc.get_val(t0+dt, x0+k3)
        
        k = (k1 + 2*k2 + 2*k3 + k4)/6
        
        return x0 + k
    
    def solve(self, t0, x0, dt, num):
        """solve dx/dt = func(t, x)
        
        Args:
            t0 (float): initial parameter
            x0 (np.array): initial values
            dt (float): step size of parameter
            num (int): iteration

        Returns:
            np.array: _description_
        """
        xc = x0
        tc = t0
        x = [xc]
        t = [tc]
        for e in range(num):
            xc = self.one_step(tc, xc, dt)
            tc = tc + dt
            if self.fnc.is_end(tc, xc):
                break
            x.append(xc)
            t.append(tc)
        return x