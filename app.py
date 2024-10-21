class Node:
    def __init__(self, concept):
        self.concept = concept.lower() 
        self.relationships = [] 

    def add_relationship(self, relation, target_node):
        self.relationships.append((relation, target_node))

    def get_relationships(self):
        
        return self.relationships


class SemanticNetwork:
    def __init__(self):
        self.nodes = []

    def add_concept(self, concept):
        for node in self.nodes:
            if node.concept == concept.lower():
                return node
        new_node = Node(concept)
        self.nodes.append(new_node)
        return new_node

    def add_relationship(self, concept1, relation, concept2):
        node1 = self.add_concept(concept1)
        node2 = self.add_concept(concept2)
        node1.add_relationship(relation, node2)

    def find_node(self, concept):
        for node in self.nodes:
            if node.concept.lower() == concept:
                return node
        return None

    def get_info(self, concept):
        node = self.find_node(concept)
        info=""
        if node:
            for relation, target in node.get_relationships():
                info += f"- {concept} {relation} {target.concept}\n"
            for rel,target in node.get_relationships():
                info += self.inherited_knowledge_with_relationship(target,concept)
            return info
        else:
            return f"Không tìm thấy khái niệm: {concept}"
    def search_by_relationship(self, concept, relation):
        node = self.find_node(concept)
        if node:
            results = []
            info=""
            for rel, target in node.get_relationships():
                if rel == relation:
                    results.append(target.concept)
            if results:
                for obj in results:
                    info += f"- {concept} {relation} {obj}\n"
            for rel,target in node.get_relationships():
                info += self.inherited_knowledge_with_relationship(target,concept)
            return info
        else:
            return f"Không tìm thấy khái niệm: {concept}"
    def inherited_knowledge_with_relationship(self, node,mainnode):
        inherited_results =""
        for rel, target in node.get_relationships():
                inherited_results+=f"- {mainnode} {rel} {target.concept} \n"
                node1=Node(target.concept)
                inherited_results += self.inherited_knowledge_with_relationship(node1,mainnode)
        return inherited_results
    def load_data(self, file_name):
        with open(file_name, "r", encoding="utf-8") as file:
            for line in file:
                concept1, relation, concept2 = line.strip().split(";")
                self.add_relationship(concept1, relation, concept2)
    def is_node(self, concept):
        return self.find_node(concept) is not None

    def is_relationship(self, concept, relation):
        node = self.find_node(concept)
        if node is not None:
            return any(rel == relation for rel, _ in node.relationships)
        return False
import tkinter as tk

class ChatbotApp:
    def __init__(self, root, network):
        self.root = root
        self.root.title("Chatbot Mạng Ngữ Nghĩa")
        self.network = network

        self.chat_area = tk.Text(root, height=20, width=50, state='disabled') 
        self.chat_area.pack()

        self.entry = tk.Entry(root, width=50)
        self.entry.pack()
        
        self.entry.bind('<Return>', self.trigger_search)

        self.button = tk.Button(root, text="Gửi", command=self.search)
        self.button.pack()

        self.load_chat_history()
    def similarity_ratio(self,string1, string2):
        """Tính toán tỷ lệ tương đồng giữa hai chuỗi."""
        # Chia chuỗi thành danh sách các từ
        words1 = set(string1.lower().split())
        words2 = set(string2.lower().split())
        
        common_words = words1.intersection(words2)
        
        return len(common_words) / max(len(words1), len(words2))
    def load_chat_history(self):
        try:
            with open("log.txt", "r", encoding="utf-8") as log_file:
                chat_history = log_file.readlines()
                self.chat_area.config(state='normal') 
                for line in chat_history:
                    self.chat_area.insert(tk.END, line)
                self.chat_area.config(state='disabled')
                self.chat_area.yview(tk.END)
        except FileNotFoundError:
            pass 
    def parse_input(self, user_input):
        parts = user_input.split(" ")
        concept = ""
        relation = None
        for i in range(len(parts)):
            potential_concept = " ".join(parts[:i + 1])

            if self.network.is_node(potential_concept):
                concept = potential_concept
                if i + 1 < len(parts):
                    next_part = parts[i + 1]
                    if self.network.is_relationship(concept,next_part):
                        relation = next_part
                        break
            else:
                continue 
        concept = concept.strip()
        return concept, relation
    def search(self):
        user_input = self.entry.get().lower()
        if user_input=="":return
        user_input = ' '.join(user_input.split()) 
        concept, relation = self.parse_input(user_input)
        info=""
        if concept:
            if relation:
                info = self.network.search_by_relationship(concept, relation)
            else:
                info = self.network.get_info(concept)
        if info=="":
                info = "Vì lý do bộ dữ liệu không đủ nên tôi không thể trả lời bạn, rất xin lỗi vì sự bất tiện này."
        else:
            filtered_responses = []
            responese=info.split("\n")
            for line in responese:
                if self.similarity_ratio(user_input, line) >= 0.5:
                    filtered_responses.append(line)
            if filtered_responses:
                info = "\n".join(filtered_responses)       
        self.log_chat(user_input, info)
        self.display_chat(user_input, info)
        self.entry.delete(0, tk.END)

    def trigger_search(self, event):
        self.button.invoke() 
    def display_chat(self, user_input, bot_response):
        self.chat_area.config(state='normal') 
        self.chat_area.insert(tk.END, f"Bạn: {user_input}\n",'user')  
        self.chat_area.insert(tk.END, f"Bot: {bot_response}\n",'bot') 
        self.chat_area.config(state='disabled') 
        self.chat_area.yview(tk.END) 

        self.chat_area.tag_config('user', foreground='black')
        self.chat_area.tag_config('bot', foreground='green')
    def log_chat(self, user_input, bot_response):

        with open("log.txt", "a", encoding="utf-8") as log_file:
            log_file.write(f"Bạn: {user_input}\n")
            log_file.write(f"Bot: {bot_response}\n")
    
if __name__ == "__main__":

    network = SemanticNetwork()
    network.load_data("data.txt")

    root = tk.Tk()
    app = ChatbotApp(root, network)
    root.mainloop()
