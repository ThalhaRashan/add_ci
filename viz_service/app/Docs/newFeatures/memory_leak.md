# Find which endpoint has the leak

1. Add a gc.collect at the end of each endpoint.   
2. Create an endpoint which:  
    1. Takes endpoint and number of times to run as input  
    2. Runs endpoint once to import warm application up  
    3. Takes snapshot one  
    4. Sends N number of request to endpoint  
    5. Take second memory snapshot.  
    6. Save comparison between snapshot in text file  
    
3. Have a look at which lines have the biggest memory changers.  
4. Set debug points to find when we call the functions  
5. Fix leak  

### Expected result:  
I think the leak will be in the data import across all endpoints because as more endpoints have been added the leak has become more prunounced.






# Endpoint memory usage

## Vizhospital

### Form
* month: 01/08/2019 - 31/07/2020  
* unitId: 5d5fa51e3a24ff00472ace57  
* n: 10
* frame rate: 15

### Usage  
Find in file vizhospital_n10



## Vizregonal

### Form
* month: 01/01/2019 - 31/07/2020  
* n: 10
* frame rate: 15

### Usage
Find in file vizregional_n10


##Completness
### Form 
* month: 01/01/2019 - 31/07/2020  
* n: 10
* frame rate: 15

### Usage
Find in file completeness_n10

### Result 
Found a leak 2.4md per 10 requests caused by a reference loop.