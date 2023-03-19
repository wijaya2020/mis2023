#pip install pytz
import datetime,pytz

dtobj1=datetime.datetime.utcnow()   #utcnow class method
print(dtobj1)

dtobj3=dtobj1.replace(tzinfo=pytz.UTC) #replace method

dtobj_hongkong=dtobj3.astimezone(pytz.timezone("Asia/Hong_Kong")) #astimezone method
print(dtobj_hongkong)