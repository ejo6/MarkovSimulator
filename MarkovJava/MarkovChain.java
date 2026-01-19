package MarkovJava;
import java.util.*;

// The Markov Chain is a directed-multigraph in an adjacency list (not matrix)
public class MarkovChain {
    // Actual graph (transition matrix, as an undirected multigraph)
    private HashMap<String, ArrayList<Edge>> chain = new HashMap<>();
    private static volatile boolean running = true; // for the long running model

    // Static class to represent edge between 2 nodes
    static class Edge {
        String toNode;
        double weight;

        public Edge(String toNode, double weight) {
            this.toNode = toNode;
            this.weight = weight;
        }
    }

    // Add vertex if not already there
    public void addVertex(String name) {
        chain.putIfAbsent(name, new ArrayList<>());
    }

    // Add new edge (main way of appending)
    public void addEdge(String from, String to, double weight) {
        // Add vertices if they dont exist
        addVertex(from); 
        addVertex(to);
        chain.get(from).add(new Edge(to, weight));
    }

    // Ensure sum of probabilities for each event = 1
    public Boolean checkGraph() {
        float sum = 0;
        for (String from : chain.keySet()) {
            for (Edge edge : chain.get(from)) {
                sum += edge.weight;
            }
            if (sum != 1) return false;
            sum = 0;
        }
        return true;
    }
    
    // Print the representation of the graph
    public void printGraph() {
        for (String from : chain.keySet()) {
            System.out.print(from + " -> ");
            for (Edge edge : chain.get(from)) {
                System.out.print("(" + edge.toNode + ", " + edge.weight + ") ");
            }
            System.out.println();
        }
    }

    // Helper for runChain
    private HashMap<String, Integer> copyChainToMap() {
        HashMap<String, Integer> result = new HashMap<>();
        for (String from : chain.keySet()) {
            result.put(from, 0);
        }
        return result;
    }

    // Run the markov chain indefinitely
    public ChainResult runChainIndefinitely(String start) throws MarkovChainException {
        // Copy values into result map
        HashMap<String, Integer> result = copyChainToMap();
        HashMap<String, Double> proportions = new HashMap<>();
        for (String state : result.keySet()) {
            proportions.put(state, 0d);
        }

        // Shut down logic
        Runtime.getRuntime().addShutdownHook(new Thread(() -> {
            System.out.println("\nCtrl+C detected. Shutting down loop...");
            running = false;
        }));

        // Loop around until were done
        String cur = start;
        if (chain.get(cur) == null) {
            throw new MarkovChainException("Start node: \"" + cur + "\" not found.");
        }

        System.out.println("Running Chain indefinitely, Ctrl+C to stop.");
        int iterations = 0;

        while (running) {
            double random = Math.random();
            double sum = 0;
            String to = "";

            for (Edge edge : chain.get(cur)) {
                sum += edge.weight;
                to = edge.toNode;
                if (random < sum) break;
            }

            cur = to;
            result.put(cur, result.get(cur) + 1); 
            iterations++;
        }
        
        for (String state : result.keySet()) {
            proportions.put(state, (double) result.get(state) / iterations);
        }

        return new ChainResult(result, proportions);
    }

    // Run the chain until it iterates out
    public ChainResult runChain(int iterations, int burnIn, String start) throws MarkovChainException {
        // Copy values into result map
        HashMap<String, Integer> result = copyChainToMap();
        HashMap<String, Double> proportions = new HashMap<>();
        for (String state : result.keySet()) {
            proportions.put(state, 0d);
        }

        // Loop around until were done
        int i = 0;        
        String cur = start;
        if (chain.get(cur) == null) {throw new MarkovChainException("Start node: \"" + cur + "\" not found.");}

        while (i < burnIn + iterations) {
            double random = Math.random();
            double sum = 0;
            String to = "";

            for (Edge edge : chain.get(cur)) {
                sum += edge.weight;
                to = edge.toNode;
                if (random < sum) break;
            }
            
            cur = to;
            i++;
            
            // Only write to results if past burn in threshold
            if (i > burnIn) {     
                result.put(cur, result.get(cur) + 1); 
            }
        }

        for (String state : result.keySet()) {
            proportions.put(state, (double) result.get(state) / iterations);
        }

        return new ChainResult(result, proportions);
    }


    // Testing
    public static void main(String[] args) {
        System.out.println("Vowel/Consonants:");
        try {
            MarkovChain chain = new MarkovChain();
            chain.addEdge("Vowel", "Consonant", 0.87);
            chain.addEdge("Vowel", "Vowel", 0.13);
            chain.addEdge("Consonant", "Vowel", 0.67);
            chain.addEdge("Consonant", "Consonant", 0.33);
            if (chain.checkGraph()) {
                chain.printGraph();
                chain.runChain(1000, 100, "Vowel").printAll();
            }
        } catch (MarkovChainException e) {
            System.err.println(e);
        }

        System.out.println("\nWeather Markov Chain:");
        try {
            MarkovChain weather = new MarkovChain();

            // States: Sunny, Cloudy, Rainy, Snowy
            weather.addEdge("Sunny", "Sunny", 0.6);
            weather.addEdge("Sunny", "Cloudy", 0.3);
            weather.addEdge("Sunny", "Rainy", 0.1);

            weather.addEdge("Cloudy", "Sunny", 0.3);
            weather.addEdge("Cloudy", "Cloudy", 0.4);
            weather.addEdge("Cloudy", "Rainy", 0.2);
            weather.addEdge("Cloudy", "Snowy", 0.1);

            weather.addEdge("Rainy", "Cloudy", 0.4);
            weather.addEdge("Rainy", "Rainy", 0.5);
            weather.addEdge("Rainy", "Sunny", 0.1);

            weather.addEdge("Snowy", "Snowy", 0.6);
            weather.addEdge("Snowy", "Cloudy", 0.3);
            weather.addEdge("Snowy", "Sunny", 0.1);

            if (weather.checkGraph()) {
                weather.printGraph();
                weather.runChainIndefinitely( "Sunny").printAll();;
            }
        } catch (MarkovChainException e) {
            System.err.println(e);
        }
    }
}