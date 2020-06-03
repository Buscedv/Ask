from flask import Flask, jsonify, abort, request

from ask import AskLibrary
app = Flask(__name__)
tasks=[
{
		'id':1,
		'title':'Buy groceries',
		'description':'Milk, Cheese, Pizza, Fruit, Tylenol',
		'done': False
},
{
		'id':2,
		'title':'Learn Python',
		'description':'Need to find a good Python tutorial on the web',
		'done': False
}
]
@app.route('/todo/api/v1.0/tasks', methods=['GET'])
def _todo_api_v1_0_tasks_GET():
	return jsonify({'tasks':tasks})
@app.route('/todo/api/v1.0/tasks/<task_id>', methods=['GET'])
def _todo_api_v1_0_tasks_task_id_get(task_id):
	task=AskLibrary.deep(tasks,{'id':task_id})
	return jsonify({'task':task})
@app.route('/todo/api/v1.0/tasks', methods=['POST'])
def _todo_api_v1_0_tasks_post():
	if( not request.json and 'title' in request.json):
		return jsonify(AskLibrary.status(400))
	task={
		'id':tasks[-1]['id']+1,
		'title':request.json['title'],
		'description':request.json['description'],
		'done': False
}
	tasks.append(task)
	return jsonify({'task':task})
@app.route('/todo/api/v1.0/tasks/<task_id>', methods=['PUT'])
def _todo_api_v1_0_tasks_task_id_put(task_id):
	task=AskLibrary.deep(tasks,{'id':task_id})
	if(len(task)==0):
		return jsonify(AskLibrary.status(404))
	if( not request.json):
		return jsonify(AskLibrary.status(404))
	if( not 'title' in request.json or 'description' in request.json or 'done' in request.json):
		return jsonify(AskLibrary.status(404))
	task=AskLibrary.quickPut(task,request.json)
	return jsonify({'task':task})
@app.route('/todo/api/v1.0/tasks/<task_id>', methods=['DELETE'])
def _todo_api_v1_0_tasks_task_id_delete(task_id):
	task=AskLibrary.deep(tasks,{'id':task_id})
	if(len(task)==0):
		return jsonify(AskLibrary.status(404))
	tasks.remove(task)
	return jsonify({'result': True })
