from model.Incident import *
import controller.controller as control

incident = Incident('jcgd','title','desc','CI1000005','1','2')

response = control.createIncident('jcgd','title','desc','CI1000005','1','2')
#print(response)
