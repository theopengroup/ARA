#=============================================================
# calculate the mean of samples
#=============================================================
def mean(v, n):
    sum=0.0     
    for i in range(0,n):
        sum = sum + v[i]
    return float(sum/n)



#=============================================================
# calculate the variance of samples
#=============================================================
def var(v, n, mean):
    sum=0.0     
    for i in range(0,n):
        sum = sum + (v[i] - mean)*(v[i] - mean)
    return float(sum/n)


#=============================================================
# calculate the autocorrelation (upto maxlag) of samples
#=============================================================
def acf(v, n, lag, mean, var):
    auto_c=0.0
    for h in range(0, n-lag):
        auto_c += (v[h]-mean)*(v[h+lag]-mean)

    auto_c /= (n-lag) #E()()

    return auto_c / var #P_lag=E()()/s^2



#=============================================================
# calculate the index of dispersion of samples
#=============================================================
def est_index_dispersion(iats, n, maxlag):
    I=0.0
    m=mean(iats, n)
    v=var(iats, n, m)
    
    for k in range(1,maxlag+1): 
        a=acf(iats, n, k, m, v)
        if (a<0):
            continue
        elif (a>1e-3):
            I+=a 
        else:
            break

    I = v*(1+2*I)/m/m

    return I
