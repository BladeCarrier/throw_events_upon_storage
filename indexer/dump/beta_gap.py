#beta_gap scratch from analysis/distfit.py
#unfinished:needs efficient beta function
beta_funcion = lambda a,b:1 #TODO:import it from somewhere
def beta_gap(x,left,right,gamma):
    gap = (x>left)*(x<right)
    q = (x-left)/(left-right)
    alpha, beta = max(0,gamma)+1,max(0,-gamma)+1
    numerator = T.pow(q,alpha-1) * T.pow((1.-q),beta-1)
    denominator = beta_function(alpha,beta)  
    return gap*numerator/denominator

