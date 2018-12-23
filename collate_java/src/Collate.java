

import java.util.*;
import java.util.stream.Collectors;

/*
 * Java version of Collate this-time-for-sure
 * @author: Ronald Haentjens Dekker
 *
 * Based on research done in the skipgram branch of CollateX.
 */
class Collate {


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
        // Sort table into common sequence list (csList)
        //   ordered by 1) number of witnesses (numerica high to low) and 2) sequence (alphabetic low to high)
        // csList = [k for k in sorted(csTable, key=lambda k: (-len(csTable[k]), k))]
        Comparator<List<String>> lengthComparator = Comparator.comparing(key -> -csTable.get(key).size());
        // NOTE: converting the array into a String is a bit ugly
        Comparator<List<String>> normalizedComparator = Comparator.comparing(key -> key.get(0)+";"+key.get(1));
        return csTable.keySet().stream().sorted(lengthComparator.thenComparing(normalizedComparator)).collect(Collectors.toList());
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