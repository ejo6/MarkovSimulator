package MarkovJava;
import java.util.HashMap;

public class ChainResult {
    HashMap<String, Integer> result;
    HashMap<String, Double> proportions;

    ChainResult (HashMap<String, Integer> result, HashMap<String, Double> proportions) {
        this.result = result;
        this.proportions = proportions;
    }

    public HashMap<String, Integer> getResult() {
        return result;
    }

    public HashMap<String, Double> getProportions() {
        return proportions;
    }
    
    public void printResults() {
        System.out.println(result.toString());
    }
    
    public void printProportions() {
        System.out.println(proportions.toString());
    }

    public void printAll() {
        System.out.println(result.toString());
        System.out.println(proportions.toString());
    }

    public String toString() {
        String result = "";
        result += result.toString() + "\n" + proportions.toString();
        return result;
    }
}
