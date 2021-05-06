import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

monday = pd.read_csv('monday.csv', sep=';')
tuesday = pd.read_csv('tuesday.csv', sep=';')
wednesday = pd.read_csv('wednesday.csv', sep=';')
thursday = pd.read_csv('thursday.csv', sep=';')
friday = pd.read_csv('friday.csv', sep=';')

DAYS = [monday, tuesday, wednesday, thursday, friday]


for day in DAYS:
    # set timestamp as datetime and as index
    day.timestamp = pd.to_datetime(day.timestamp)
    day.set_index('timestamp', inplace=True)

    # Kick out customers that do not check out
    all_customers = set(day.customer_no.values)
    checked_out_customers = set(day[day['location'] == 'checkout'].customer_no.values)
    non_checked_out_customers = list(all_customers.difference(checked_out_customers))
    day = day[~day.loc[:, 'customer_no'].isin(non_checked_out_customers)]
    print(f'''The customers that have not checked out on {day.index[0].day_name()} are {non_checked_out_customers}''')

for day in DAYS:
    # add the customer count
    day['nr_loc'] = day.groupby('customer_no').cumcount()
    add_customer = day.loc[:, 'nr_loc'].transform(lambda x: 1 if x == 0 else 0)
    delete_customer = day.loc[:, 'location'].transform(lambda x: -1 if x == 'checkout' else 0)
    day['add'] = add_customer + delete_customer
    day['cust_total'] = day.loc[:, 'add'].cumsum()


monday.info()
monday.head()
monday.tail()

# Add the day
monday['day'] = 'monday'
tuesday['day'] = 'tuesday'
wednesday['day'] = 'wednesday'
thursday['day'] = 'thursday'
friday['day'] = 'friday'

# combine the DataFrames
total = monday.append(tuesday.append(wednesday.append(thursday.append(friday))))
total.shape
total.head()

### Use resample to make it easier to calculate the nr. of customers at each point
### in time 
total.columns
total = total.groupby(['customer_no', 'day']).resample('min').ffill()

total.index = total.index.droplevel([0, 1])

# Inspect the count per location
total.groupby('location')['customer_no'].count()
total.groupby(by=[total.index.day, total.index.hour, total.index.hour, 'location'])['customer_no'].count()


### Display the number of customers at checkout over time

total.groupby(by=[total.index.day, total.index.hour, 'location'])['customer_no'].count().unstack(2)['checkout'].plot(kind='bar')
plt.figure(figsize=(20, 20))
plt.show()


### Calculate the time each customer spent in the market

time_ = total.reset_index()
time_in_market = time_.groupby(['customer_no', 'day'])[['timestamp']].last() - time_.groupby(['customer_no', 'day'])[['timestamp']].first()
time_in_market['counter'] = 1
time_in_market.head()
time_in_market['time_spent'] = time_in_market.timestamp.dt.seconds/60
time_in_market.hist(column='time_spent', figsize=(12, 8), bins=50)
plt.xlabel('Time spent in minutes')
plt.ylabel('Nr. of customers')
plt.title('Distribution of time spent in the supermarket')
plt.show()


time_count = time_in_market.groupby('timestamp').count()
time_count.shape
time_count.reset_index(inplace=True)
time_count['time_spent'] = time_count.timestamp.dt.seconds/60
time_count.head()


time_count.plot(x='time_spent', y='counter', figsize=(12, 8))#.bar(x='timestamp', height='count')
plt.xlabel('Time spent in minutes')
plt.ylabel('Nr. of customers')
plt.title('Distribution of time spent in the supermarket')
plt.show()

#time_count.time_spent.value_counts()
time_count.shape


### Calculate the total number of customers present in the supermarket over time.

# make sure each customer only enters the supermarket max once a day
total[total.location == 'checkout'].groupby(['customer_no', 'day']).count().max()
len(set(monday.customer_no.values).difference())
len(set(monday[monday.location == 'checkout'].customer_no.values))

# plot number of totatl customers
total.reset_index().plot(x='timestamp', y='cust_total', figsize=(12, 8))


# Create a plot with average nr. of customers per time over one day
# Group by timestep
daily = total.reset_index()
daily.timestamp = daily.timestamp.transform(lambda x: x.time())
daily.head()


daily.groupby('timestamp')['cust_total'].mean().reset_index().plot(x='timestamp', y='cust_total', figsize=(12, 8))


# ### Our business managers think that the first section customers visit follows a different pattern than the following ones. Plot the distribution of customers of their first visited section versus following sections (treat all sections visited after the first as “following”).

total_firsts = total[total['add']==1].shape[0]
freq_firsts = total[total['add']==1].groupby('location').count()['customer_no']/total_firsts
freq_firsts.plot.bar(figsize=(12, 8))
plt.axis(ymin=0, ymax=1)
plt.show()


total_seconds = total[total['add']!=1].shape[0]
freq_seconds = total[total['add']!=1].groupby('location').count()['customer_no']/total_seconds
#freq_firsts.plot.bar(figsize=(12, 8), color='r')
freq_seconds.plot.bar(figsize=(12, 8))
plt.axis(ymin=0, ymax=1)
plt.show()


pd.DataFrame([freq_firsts, freq_seconds], index=['first', 'second']).transpose().plot.bar(figsize=(12, 8))
plt.title('Frequency of section transitioned into by being a new customer ("first") or not ("second")')
plt.xlabel('Section')
plt.ylabel('Frequency of choice')
plt.show()


# ### Estimate the total revenue for a customer value using the following table:

prices = pd.DataFrame(index=['fruit', 'spices', 'dairy', 'drinks'], columns=['revenue per minute in €'], data=[4, 3, 5, 6])
prices


# Calculate the average time per customer spent in each section


minutes_spent = total.reset_index()
minutes_spent.head()


#minutes_spent['time'] = minutes_spent.timestamp.transform(lambda x: x.time())
minutes_spent['day'] = minutes_spent.timestamp.apply(lambda x: x.day)
#minutes_spent.head()


g = minutes_spent.groupby(['customer_no', 'day'])


minutes_spent['time_next'] = minutes_spent.groupby(['customer_no', 'day'])['timestamp'].transform(lambda x: x.shift(-1, fill_value=0)-x)
minutes_spent['time_next'] = minutes_spent.time_next.transform(lambda x: int(x.seconds/60))
minutes_spent.head(10)


# int(minutes_spent.time_next[0].seconds/60)


# Calculate average time spent by section
minutes_spent.groupby('location')['time_next'].mean()


# Actually look at the distribution first
for group, df_group in minutes_spent.groupby('location')['time_next']:
    print(df_group.hist(bins=20))
    plt.axis(xmax=40)
    plt.show()


#### Calculate the initial state probabilities

freq_firsts.to_csv('initial_probabilities.csv')

#### Calculate the transition probabilities

total['transition'] = total.groupby(['day', 'customer_no'])['location'].shift(-1).fillna('checkout')
P = pd.crosstab(total[total['add']!=1]['location'], total[total['add']!=1]['transition'], normalize=0)
assert all(P.sum(axis=1))==1
P.to_csv('transition_probability_matrix.csv')

P