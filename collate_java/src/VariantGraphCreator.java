import java.util.*;

/* Variant graph creator
 *
 * @author: Ronald Haentjens Dekker
 * Date: 25-10-2018
 *
 * This class is an iterative variant graph builder
 * The order in which tokens are supplied to this builder
 * determines whether tokens are grouped together in a node or not.
 * The order of tokens within a witness is maintained at all times.
 *
 */


/* Version 3
 * We create we a list of nodes in an order that is similar to the topological sort of the nodes of the variant
 * graph
 *
 * Insertion of a node
 * Input: We have a token (with a witness identifier and a position in the witness)
 * and the token of has a normalized form.
 *
 * Algorithmic steps:
 * 1. Filter the nodes of the list on the witness identifier..
 * 1b NOTE: that the start and the end vertices are always a special code (everything is higher than the start
 *    vertex and everything is lower than the end vertex).
 * 2. Navigate the existing nodes using a comparator, not on the identifier but on token position
 * 3. Find the node a bit lower and the node a bit higher
 * 4. Look at the nodes in between the lower and the higher using the normalized form.
 * 5. If not a normalized form match.. insert a new node
 *      This happens if a witness is th first to add a normalized form thereby creating a new column
 *      or in case of a transposition multiple nodes need to be created.
 * 6. If yes add token to that node
 */

public class VariantGraphCreator {
//    VariantGraph variantGraph;
//    List<VariantGraph.Vertex> verticesListInTopologicalOrder;
//
//    VariantGraphCreator() {
//        this.variantGraph = new VariantGraph();
//        this.verticesListInTopologicalOrder = new ArrayList<>();
//        this.verticesListInTopologicalOrder.add(variantGraph.getStart());
//        this.verticesListInTopologicalOrder.add(variantGraph.getEnd());
//    }

    static class Node {
        String normalized;
        Map<String, Integer> witnessIdToPosition = new HashMap<>();

        Node(String normalized) {
            this.normalized = normalized;
        }

        @Override
        public String toString() {
            return normalized;
        }
    }

    static List<VariantGraphCreator.Node> initList() {
        List<VariantGraphCreator.Node> verticesListInTopologicalOrder = new ArrayList<>();
        verticesListInTopologicalOrder.add(new Node("# start"));
        verticesListInTopologicalOrder.add(new Node("# end"));
        return verticesListInTopologicalOrder;
    }

    // a witness is supplied
    // Token is a witness id plus a pointer to a location within a witness
    static void insertTokenInVariantGraph(List<Node> verticesListInTopologicalOrder, String witnessId, int position, String value) {
        // This method should return two vertices: one that is higher than the one we want to insert
        // and one that is lower.
        int lower = 0; // start node
        int higher = verticesListInTopologicalOrder.size()-1;

        // rule 1b: start and end vertices are special
        // Although this is more of a fast path; if we remove this two conditions
        // it should still work
        // We skip the start node (lower+1) and the end node (< higher)
        for (int pos = lower +1; pos < higher; pos++) {
            Node v = verticesListInTopologicalOrder.get(pos);
            // Rule 1: If V does not contain the witness that we are looking for then skip
            if (!v.witnessIdToPosition.containsKey(witnessId)) {
                continue;
            }
            // Do the actual token comparison
            int bla = v.witnessIdToPosition.get(witnessId) - position;
            if (bla < 0) {
//                System.out.println("token "+token+" is higher than "+theOtherToken);
                lower = pos;
                continue;
            }
            if (bla > 0) {
//                System.out.println("token "+token+" is lower than "+theOtherToken);
                higher = pos;
                break;
            }

        }

        // we need to decide whether we need to create a new vertex or not
        // we search in between the lower and the upper bound to see whether there is a vertex
        // that has the same
//        System.out.println("Token: "+token+" ; Lower: "+lower+" ; higher: "+higher);




        if (higher-lower == 1) {
            // lower and higher tokens are right next to each other.
            // We have to add a new node in the variant graph
            // NOTE: here there is no difference between inserting before the upper and after the lower bound!
            createVertexForTokenInsertBefore(witnessId, position, value, higher, verticesListInTopologicalOrder);
            return;
        }

        // there is a gap between lower and higher
        // search for a node that has the same normalized form as the token we want to place
        // NOTE: implementation detail; we could have done this while we were looping above; but then we would
        // have to done more string comparisons.

        // Search to see whether we need to create a new vertex or not
        Node result = null;
        for (int x=lower+1; x < higher; x++) {
            Node n = verticesListInTopologicalOrder.get(x);
            // all the tokens at one vertex have the same normalized form
            // TODO: we would normalize the value of the token here when we start to use nromalizers!
            if (n.normalized.equals(value)) {
                result = n;
                break;
            }
        }

        // This happens when there is a node at a rank that is between lower and higher
        // but is not a normalized form match.
        // This will lead to a column with variation in the alignment table
        // Or to multiple nodes on the same rank un the variant graph.
        // So there already is a rank in the graph or a column in the tale
        // And need to add it to that.
        // TODO: replace this exception with useful commentary.
        // throw new RuntimeException("While trying to place "+token+" \n We searched for a normalized form match within the window "+(i+1)+"-"+(j-1)+", but could not find anything!");

        // NOTE: We do an insert before upper bound here!
        if (result==null) {
            createVertexForTokenInsertBefore(witnessId, position, value, higher, verticesListInTopologicalOrder);
            return;
        }

        // We searched within the window of potential normalized matches and we did find a normalized match.
        // Add this token to the existing vertex.
        result.witnessIdToPosition.put(witnessId, position);

    }

    /*
     * creates a new vertex for a token
     * and inserts it in the topological prdered list of the vertices
     * where i stands for the position in the list
     * NOTE: we could at a method for when the i is not known
     * but I don't think that will happen often.
     * This maybe confusing to callers of this method
     * Although of course this is a private method.
     */
    private static void createVertexForTokenInsertBefore(String witnessId, int position, String value, int higher, List<Node> verticesListInTopologicalOrder) {
        Node node = new Node(value);
        node.witnessIdToPosition.put(witnessId, position);
        verticesListInTopologicalOrder.add(higher, node);
    }

//    @Override
//    public String toString() {
//        return verticesListInTopologicalOrder.toString();
//    }
}




    // method to create node for token and insert it in topological list after the lower bound.
//     * NOTE2: pay attention to +1.
    //    private void createVertexForToken(SimpleToken token, int i) {
//        VariantGraph.Vertex vertex = new VariantGraph.Vertex(variantGraph);
//        vertex.tokens().add(token);
//        verticesListInTopologicalOrder.add(i+1, vertex);
//    }

    /*
      This method takes the topological sort list of vertices and adds all the edges where
      needed

      This is of course used for the final graph
      But also to visualize the intermediate graphs.

     */
    // About the edges
    // First point:
    // Since the graph is only partially build one might think that it is not possible to
    // add edges, but turns out to be not a problem because the nodes are sorted in topological order and
    // for each witness we know the previous node.
    // Second point: the edges need to be reconnected the second and third times.
    // It seems that the implementation of the variant graph connect method already takes care of this.
    // But only partly. To fix this we clear each vertex before adding relations to it.

//    public void addEdges() {
//        /* We traverse over the topological order list
//         * Of course skip the start node
//         * then for every node...
//         *
//         * We should maybe first clear the incoming and outgoing edges when we first visit a node
//         * That way we can use this code to visualize multiple partial variant graphs.
//         */
//        /*
//         * The clearing out we do later on...
//         */
//
//        // we find a vertex
//        // the vertex contains tokens for one or more witnesses
//        // now each of these witnesses need to have a valid path
//        // from the previous vertex of that witness to the current vertex.
//        // so we create a map that contains the last seen vertex for eahc witness
//        // at the start that is of course the start vertex.
//        Map<Witness, VariantGraph.Vertex> witnessToLastVertexMap = new HashMap<>();
//
//        for (VariantGraph.Vertex v : verticesListInTopologicalOrder) {
//            // skip the start vertex
//            if (v == variantGraph.getStart()) {
//                continue;
//            }
//            // NOTE: oh the end vertex has no tokens
//            if (v == variantGraph.getEnd()) {
//                for (Map.Entry<Witness,VariantGraph.Vertex> witnessIdToPreviousVertexEntry : witnessToLastVertexMap.entrySet()) {
//                    Witness witness = witnessIdToPreviousVertexEntry.getKey();
//                    VariantGraph.Vertex pre = witnessIdToPreviousVertexEntry.getValue();
//                    variantGraph.connect(pre, v, Collections.singleton(witness));
//                }
//                break;
//            }
//
//            // remove all the existing relations on this vertex.
//            v.clear();
//
//            // nu moet ik alle tokens van een vertex af gaan om te kijken welke witnesses er allemaal
//            // op staan.
//            for (Token t: v.tokens()) {
//                VariantGraph.Vertex previous = witnessToLastVertexMap.getOrDefault(t.getWitness(), variantGraph.getStart());
//                // NOTE: does connect work if it is called for the same vertex multiple times?
//                // I guess so?
//                variantGraph.connect(previous, v, Collections.singleton(t.getWitness()));
//                // nu moet ik natuurlijk die map bijwerken
//                witnessToLastVertexMap.put(t.getWitness(), v);
//            }
//        }
//    }









/*
 * We need a node comparator
 * that after checking the witness identifier overlap ( de smallest set has to be present in the fuller set)
 * delegates to a token comparator based on position to do the rest. Simple Token Comparator has that.
 *
 * We could create a node witness view.
 */


/*
 * Version 2 of the variant graph builder based on skipgrams
 * The idea here is to first create a list of tokens in what will be the topological sort of the nodes
 * of the variant graph.
 *
 * After the list of tokens is created in the right order nodes can be created from the list
 * bij deduplicating the tokens.. then the edges can be created... Sounds like a plan.
 *
 * We use a single navigableMap (either a treemap or skiplist) to accomplish this goal
 *
 *
 *
 *
 *

 */



//    /*
//    * We need a a key object that is comparable that is a composite of a witness id and a comparable token
//    * so we create an object for it..
//    * Not a key any more just a list..
//    */
//
//    public static class TokenComparatorThatAcceptsTokensFromMultipleWitnesses implements Comparator<SimpleToken> {
//        // first we check whether the tokens are of the same witness
//        // if not, we return -1.
//        // If there are from the same witness we call the compare function on the SimpleToken class itself.
//        // pretty simple concept.
//        @Override
//        public int compare(SimpleToken o1, SimpleToken o2) {
//            int result = o1.getWitness().getSigil().compareTo(o2.getWitness().getSigil());
//            if (result != 0) return result;
//            return o1.compareTo(o2);
//        }
//    }



