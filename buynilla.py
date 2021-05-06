import pandas as pd
import os
import numpy as np

def read_concat_data():

    df = pd.DataFrame() # create an empty dataframe
    weeks = os.listdir('./data') # list all files at the data folder
    current = os.getcwd() # get the current path
    for i in weeks: # create loop to get all csv files within the data folder one by one and merge them
        df_new = pd.read_csv(current + '/data/' +i, sep = ';', parse_dates = True, index_col=0)
        df = pd.concat([df, df_new])
    df = df.sort_values(['timestamp']) # sort the index 
    
    #normally customer numbers start from 1 at each five days! however, these customers different although their numbers are same. Therefore, created a new column customer_id. here all customers are unique!
    df['customer_id'] = df['customer_no']  # create a customer_id column in which the customers will be unique throughout days    
    for i in df.index.day.unique(): # go to each day 
        rowIndex = df.index[df.index.day > i] # receive the index numbers of each row higher than the day of concern
        df.loc[rowIndex,'customer_id'] = df.loc[rowIndex,'customer_id'] + df[df.index.day == i]['customer_no'].max() # incrementally add max customer number of a day to the day after it 
    
    #create a section_order column: 
    # for the first location - first
    enter_datetimes = df.reset_index().groupby("customer_id")["timestamp"].min()
    for customer in df["customer_id"].unique():
        df.loc[(df.customer_id == customer) & (df.index == enter_datetimes[customer]),
        "section_order"] = "first"
    #for the checkout - checkout
    df.loc[df["location"] == "checkout", "section_order"] = "checkout"

    # for the other locations - following
    df["section_order"].fillna("following", inplace=True)

    return df


def data_exploration():
    # data exploration is performed at data_exploration_supermarket.ipynb
    ...

def transition_probability_matrix(df):
    '''calculates the transition probability matrix of customer transitions from one section to other'''
    df['transition'] = df.groupby('customer_id')['location'].shift(-1) # shift the location column by one per customer and assign it to a new column called transition
    df = df.fillna('checkout') # fill the created one missing value at shift step by 'checkout'
    P = pd.crosstab(df['location'], df['transition'], normalize='index') # calculate transition probability matrix
    return(P)

def location_finder(customer_id, df):
    location = df[(df['customer_id'] == customer_id)&(df['section_order']=='first')]['location'][0]
    return location

class Customer:
    '''a single customer that moves through the supermarket in a MCMC simulation'''

    def __init__(self, id):
        self.id = id
        self.location = location_finder(2, df)

    def __repr__(self):
        return f'Customer {self.id} is in {self.location}'

    def next_location(self):
        '''proparagates the customer to the next state'''
        current_state = self.location # define the current state
         # find the transition probability
        state_space = ['checkout','dairy','drinks','fruit','spices'] #possible states
        P = transition_probability_matrix(df)
        self.location = np.random.choice(state_space, p = P.loc[cust1.location]) # could not yet understand np.dot thing completely! - please double check this step
        return self.location
        

df = read_concat_data()
cust1 = Customer(1)
print(cust1.__repr__())
print(f"Customer's next location is {cust1.next_location()}")