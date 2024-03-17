import ollama, os

def gen_model_from_modelfile(name, base_path, start_function: callable=lambda: None, end_function: callable=lambda: None):
	start_function()

	with open(os.path.join(os.path.dirname(base_path), 'modelfiles', name)) as file:
		ollama.create(model=name, modelfile=file.read())
	
	end_function()