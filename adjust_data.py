import random

import pandas as pd
import re
#
#
# prev_data = pd.read_csv('final_data1.csv')
#
# ingredient = prev_data['ingredient']
# dirty_ing = prev_data['Ingredients']
#
#
# def process(x):
#     ing_l = eval(x['ingredient'])
#     dirty_ing_l = eval(x['Ingredients'])
#     final_l = []
#     for i in ing_l:
#         for j in dirty_ing_l:
#             if i in j.lower():
#                 new_l = [i]
#                 number = re.findall(r"\d+",j)
#                 if number:
#                     res = int(number[0])*100
#                 else:
#                     res = 350
#                 new_l.append(res)
#                 final_l.append(new_l)
#                 break
#     x['ingredients_num'] = final_l
#     print(final_l)
#     return x
#
# prev_data = prev_data.apply(lambda x:process(x),axis=1)
#
#
# print(type(prev_data))
#
# prev_data.to_csv('final_data1.csv')

df = pd.read_csv('final_data1.csv')
person = pd.read_csv('persondetail.csv')
person['Published_meals'] = person['Published_meals'].map(lambda x: [])
df['contributor_id'] = 0
df['contributor_id'] = df['contributor_id'].map(lambda x: random.randint(1,6))


count = 0
def add_publish(x,person):
    global count
    person_id = int(x['contributor_id'])
    count += 1
    person.iloc[person_id-1]['Published_meals'] = person.iloc[person_id-1]['Published_meals'].append(count)
    return x
df = df.apply(lambda x:add_publish(x,person),axis=1)

person.to_csv('persondetail.csv')
df.to_csv('final_data1.csv')
