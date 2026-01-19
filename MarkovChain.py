import os
import random
import pandas as pd
import matplotlib.pyplot as plt

CSV_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "csv_output")

class MarkovChainException(Exception):
    pass

class Edge:
    def __init__(self, toNode: str, weight: float):
        self.toNode = toNode
        self.weight = weight

class MarkovChain:
    def __init__(self):
        self.chain: dict[str, list[Edge]] = {}

    def addVertex(self, name: str):
        self.chain.setdefault(name, [])
    
    def addEdge(self, fromNode: str, toNode: str, weight: float):
        self.addVertex(fromNode)
        self.addVertex(toNode)
        self.chain[fromNode].append(Edge(toNode, weight))

    def checkGraph(self) -> bool:
        for fromNode in self.chain.keys():
            weight_sum = 0.0
            for edge in self.chain[fromNode]:
                weight_sum += edge.weight
            if abs(weight_sum - 1.0) > 1e-9:
                return False
        return True
    
    def printGraph(self): 
        for fromNode in self.chain.keys():
            print(f"{fromNode} -> ", end="")
            for edge in self.chain[fromNode]:
                print(f"({edge.toNode}, {edge.weight}) ", end="")
            print()

    def copyChainToMain(self) -> dict[str, int]:
        return {fromNode: 0 for fromNode in self.chain.keys()}

    def _resolve_csv_path(self, csv_path: str) -> str:
        if os.path.dirname(csv_path):
            return csv_path
        os.makedirs(CSV_DIR, exist_ok=True)
        return os.path.join(CSV_DIR, csv_path)

    def runChainIndefinite(self, start: str, write_interval: int = 0) -> dict[str, int]:
        result = self.copyChainToMain()
        i = 0 # track interations incase we're writing to csv

        cur = start
        if self.chain.get(cur) is None:
            raise MarkovChainException(f'Start node: "{cur}" not found.')
        csv_path = self._resolve_csv_path("convergence.csv")
        try:
            while True:
                random_num = random.random()
                weight_sum = 0.0
                to = ""
                for edge in self.chain[cur]:
                    weight_sum += edge.weight
                    to = edge.toNode
                    if random_num < weight_sum:
                        break
                cur = to
                result[cur] = result[cur] + 1

                if write_interval != 0 and i % write_interval == 0:
                    result_df = pd.DataFrame([result])
                    result_df.insert(0, "Iteration", i)
                    write_header = (not os.path.exists(csv_path)) or os.path.getsize(csv_path) == 0
                    result_df.to_csv(csv_path, mode="a", header=write_header, index=False)

                i += 1
        except KeyboardInterrupt:
            print("\nCtrl+C detected. Shutting down loop...")

        print(result)
        return result

    def runChainIterations(self, iterations: int, start: str, burnIn: int = 0, write_interval: int = 0, csv_path: str = "convergence.csv",) -> tuple[dict[str, int], dict[str, float]]:
        # Initialize self
        result = self.copyChainToMain()
        proportions = {}
        for state in result.keys():
            proportions[state] = 0

        i = 0
        cur = start
        if self.chain.get(cur) is None:
            raise MarkovChainException(f'Start node: "{cur}" not found.')

        csv_path = self._resolve_csv_path(csv_path)
        if write_interval != 0:
            self._csv_cleanup(csv_path)

        while i < iterations:
            random_num = random.random()
            weight_sum = 0.0
            to = ""

            for edge in self.chain[cur]:
                weight_sum += edge.weight
                to = edge.toNode
                if random_num < weight_sum:
                    break

            cur = to
            i += 1
            
            # Only write to results if past burn in threshold
            if i > burnIn: result[cur] = result[cur] + 1

            # Logic for csv
            if write_interval != 0 and i % write_interval == 0:
                result_df = pd.DataFrame([result])
                result_df.insert(0, "Iteration", i)
                write_header = (not os.path.exists(csv_path)) or os.path.getsize(csv_path) == 0
                result_df.to_csv(csv_path, mode="a", header=write_header, index=False)            

        for state in result.keys():
            proportions[state] = result[state] / iterations

        print(result)
        print(proportions)
        return result, proportions
    
    def _csv_cleanup(self, csv_path: str):
        csv_path = self._resolve_csv_path(csv_path)
        open(csv_path, "w").close()

    def graph_results(self, csv_path: str = "convergence.csv"):
        csv_path = self._resolve_csv_path(csv_path)
        if (not os.path.exists(csv_path)) or os.path.getsize(csv_path) == 0:
            print("No data to graph.")
            return
        df = pd.read_csv(csv_path)
        x = "Iteration"
        y_cols = [col for col in df.columns if col != x]
        totals = df[y_cols].sum(axis=1)
        proportions = df[y_cols].div(totals, axis=0)
        proportions.insert(0, x, df[x])
        proportions = proportions.sort_values(by=x)
        proportions.plot(x=x, y=y_cols, kind="line", marker="o")
        plt.xlabel("Iterations")
        plt.ylabel("Proportion")
        plt.title("Markov Chain Convergence (Proportions)")
        plt.tight_layout()
        plt.show()
    

if __name__ == "__main__":
    print("Vowel/Consonants:")
    try:
        chain = MarkovChain()
        chain.addEdge("Vowel", "Consonant", 0.87)
        chain.addEdge("Vowel", "Vowel", 0.13)
        chain.addEdge("Consonant", "Vowel", 0.67)
        chain.addEdge("Consonant", "Consonant", 0.33)
        if chain.checkGraph():
            chain.printGraph()
            chain.runChainIterations(1000, "Vowel", burnIn=100, write_interval=10, csv_path="convergence_vowel.csv")
            chain.graph_results(csv_path="convergence_vowel.csv")
    except MarkovChainException as e:
        print(e)

    print("\nWeather Markov Chain:")
    try:
        weather = MarkovChain()

        weather.addEdge("Sunny", "Sunny", 0.6)
        weather.addEdge("Sunny", "Cloudy", 0.3)
        weather.addEdge("Sunny", "Rainy", 0.1)

        weather.addEdge("Cloudy", "Sunny", 0.3)
        weather.addEdge("Cloudy", "Cloudy", 0.4)
        weather.addEdge("Cloudy", "Rainy", 0.2)
        weather.addEdge("Cloudy", "Snowy", 0.1)

        weather.addEdge("Rainy", "Cloudy", 0.4)
        weather.addEdge("Rainy", "Rainy", 0.5)
        weather.addEdge("Rainy", "Sunny", 0.1)

        weather.addEdge("Snowy", "Snowy", 0.6)
        weather.addEdge("Snowy", "Cloudy", 0.3)
        weather.addEdge("Snowy", "Sunny", 0.1)

        if weather.checkGraph():
            weather.printGraph()
            weather.runChainIterations(1000, "Sunny", 10, write_interval=10, csv_path="convergence_weather.csv")
            weather.graph_results(csv_path="convergence_weather.csv")
    except MarkovChainException as e:
        print(e)
