

import java.io.BufferedReader;
import java.io.FileInputStream;
import java.io.IOException;
import java.io.InputStreamReader;
import java.util.*;
import java.util.stream.Collectors;

/*
 * Java version of Collate this-time-for-sure
 * @author: Ronald Haentjens Dekker
 *
 * Based on research done in the skipgram branch of CollateX.
 */
class Collate {


    public static String readTextFile(String filename) throws IOException {
        // Open the file
        FileInputStream fstream = new FileInputStream(filename);
        BufferedReader br = new BufferedReader(new InputStreamReader(fstream));

        StringBuilder result = new StringBuilder();
        String strLine;

        //Read File Line By Line
        while ((strLine = br.readLine()) != null)   {
            // Print the content on the console
            //System.out.println (strLine);
            result.append(strLine);
        }

        //Close the input stream
        br.close();
        return result.toString();
    }


    public static void collate(Map<String, List<String>> witnessData) {
        Map<List<String>, List<Collate.Skipgram>> commonSequenceTable = Collate.createCommonSequenceTable(witnessData);

        // We create a function that calculates the uniqueness of each key in the common sequence table
        Map<List<String>, Collate.AnalyticResult> uniquenessFactor = Collate.analyse(commonSequenceTable);


        // the reasoning during the creation of the priority list is too simple
        // we first need to gather more info to be able to able to make better decisions.
        List<List<String>> commonSequencePriorityList = Collate.createCommonSequencePriorityList(commonSequenceTable);

        // Diagnostic output
        for (List<String> key : commonSequencePriorityList) {
            System.out.println(String.join(" ", key) + " " + uniquenessFactor.get(key)+" "+commonSequenceTable.get(key));
        }

        // we create the topological ordered list
        // by selecting one skip bigram from the common sequence priority list
        List<VariantGraphCreator.Node> topologicalList = VariantGraphCreator.initList();


        for (List<String> normalizedBigram : commonSequencePriorityList) {
            // get the actual bigrams from the CST
            List<Collate.Skipgram> skipgrams = commonSequenceTable.get(normalizedBigram);

            for(Collate.Skipgram skipgram : skipgrams) {
                selectSkipgram(skipgram, witnessData, topologicalList);
            }
        }

        System.out.println(topologicalList);



    }

    private static void selectSkipgram(Collate.Skipgram skipgram, Map<String, List<String>> witnessData, List<VariantGraphCreator.Node> topologicalList) {
        // we must look for the location where to insert the vertex
        // we have to get the tokens out of the bigram
        // this method has to be called twice. Once for each token in the skipgram
        String witnessId = skipgram.witnessId;
        int position = skipgram.first;
        String value = witnessData.get(witnessId).get(position);
        VariantGraphCreator.insertTokenInVariantGraph(topologicalList, witnessId, position, value);

        position = skipgram.second;
        value = witnessData.get(witnessId).get(position);
        VariantGraphCreator.insertTokenInVariantGraph(topologicalList, witnessId, position, value);
    }



//    Sample data
//    witnessData = {'wit1': ['a', 'b', 'c', 'd', 'e'], 'wit2': ['a', 'e', 'c', 'd'], 'wit3':['a', 'd', 'b']}


    public static void main(String[] args) {
        Map<String, List<String>> witnessData = new LinkedHashMap<>();
        witnessData.put("wit1", Arrays.asList("a", "b", "c", "d", "e"));
        witnessData.put("wit2", Arrays.asList("a", "e", "c", "d"));
        witnessData.put("wit3", Arrays.asList("a", "d", "b"));
        Map<List<String>, List<Skipgram>> csTable = createCommonSequenceTable(witnessData);
        List<List<String>> csList = createCommonSequencePriorityList(csTable);

        // Diagnostic output
        for (List<String> key : csList) {
            System.out.println(key +" "+csTable.get(key));
        }
    }

    static List<List<String>> createCommonSequencePriorityList(Map<List<String>, List<Skipgram>> csTable) {
        // Sort the common table into a common sequence priority list
        // ordered by 1) number of witnesses (numerica high to low),
        //            2) by uniqueness of the sequence (high to low),
        //            3) alphabetic (low to high, a-z)

        // calculate uniqueness for each of the sequences.
        // NOTE: Some design notes follow
        // I could also provide the uniquess fadctor sepearat;y
        // But then that would make things more complicated.
        // If I make the return value of this method a bit more complicated
        // so that the uniqueness factor is included in the result.
        // Or I could create a method that creates an extended version of the common sequence table
        // with the uniqueness factor included in the keys.
        // For now I could also calculate the uniqueness factor twice.


        // some decision making notes:
        // in case of low depth and low uniqueness it is not really sure which one is the better parameter to work with
        Map<List<String>, AnalyticResult> uniquenessFactorMap = analyse(csTable);

        Comparator<List<String>> depthComparator = Comparator.comparing(key -> -uniquenessFactorMap.get(key).depth);
        Comparator<List<String>> uniquenessComparator = Comparator.comparing(key -> -uniquenessFactorMap.get(key).uniqueness);
        // NOTE: converting the array into a String is a bit ugly
        Comparator<List<String>> normalizedComparator = Comparator.comparing(key -> key.get(0)+";"+key.get(1));
        return csTable.keySet().stream().sorted(depthComparator.thenComparing(uniquenessComparator).thenComparing(normalizedComparator)).collect(Collectors.toList());
    }

    static Map<List<String>, List<Skipgram>> createCommonSequenceTable(Map<String, List<String>> witnessData) {
        // Construct common sequence table (csTable) of all witnesses as dict
        // key is skipbigram
        // value is list of (siglum, pos1, pos2) tuple, with positions of skipgram characters
        Map<List<String>, List<Skipgram>> csTable = new HashMap<>();
        for (Map.Entry<String, List<String>> entry : witnessData.entrySet()  ) {
            for (int first=0; first < entry.getValue().size(); first++) {
                for (int second = first+1; second < entry.getValue().size(); second++) {
                    List<String> normalized = new ArrayList<>();
                    normalized.add(entry.getValue().get(first));
                    normalized.add(entry.getValue().get(second));
                    Skipgram skipgram = new Skipgram(entry.getKey(), first, second);
                    csTable.computeIfAbsent(normalized, e -> new ArrayList<>()).add(skipgram);
                }
            }
        }
        return csTable;
    }

    // This thing should return the depth as well as the uniqueness of each key

    static Map<List<String>, AnalyticResult> analyse(Map<List<String>, List<Collate.Skipgram>> commonSequenceTable) {
        Map<List<String>, AnalyticResult> uniqunessValuePerNormalizedBigram = new HashMap<>();
        for (List<String> normalizedBigram : commonSequenceTable.keySet()) {
            // it might be better to go over the entries instead, oh well, later
            List<Collate.Skipgram> skipgrams = commonSequenceTable.get(normalizedBigram);
            // we have to count the number of different witnesses this normalized skipgram occurs in.
            // We do that by creating of a set of all the witness identifiers the skipgrams that this key is associated with
            Set<String> witnessIds = new HashSet<>();
            for (Collate.Skipgram skipgram : skipgrams) {
                witnessIds.add(skipgram.witnessId);
            }
            AnalyticResult analyticResult = new AnalyticResult();
            analyticResult.uniqueness = (float) witnessIds.size() / skipgrams.size();
            analyticResult.depth = witnessIds.size();
            uniqunessValuePerNormalizedBigram.put(normalizedBigram, analyticResult);
        }
        return uniqunessValuePerNormalizedBigram;
    }

    static class AnalyticResult {
        int depth; // number of witnesses a pattern occurs in.
        float uniqueness; // 1 means pattern is completely uniqueness with a witness

        @Override
        public String toString() {
            return depth+":"+uniqueness;
        }
    }

    static class Skipgram {
        String witnessId;
        int first;
        int second;

        public Skipgram(String witnessId, int first, int second) {
            this.witnessId = witnessId;
            this.first = first;
            this.second = second;
        }

        @Override
        public String toString() {
            return this.witnessId+", "+this.first+", "+this.second;
        }
    }
}