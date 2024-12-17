package main

import (
	"bufio"
	"flag"
	"fmt"
	"log"
	"os"
	"strconv"
	"strings"
	"sync"
	"time"
)

var hashWorker int
var dataWorker int
var compWorker int
var input string

func init() {
	flag.IntVar(&hashWorker, "hash-workers", 0, "<number of hash workers to hash BSTs>")
	flag.IntVar(&dataWorker, "data-workers", 0, "<number of workers to update the map>")
	flag.IntVar(&compWorker, "comp-workers", 0, "<number of workers to do the comparisons>")
	flag.StringVar(&input, "input", "", "<path to input file>")
	flag.Parse()
}

type Tree struct {
	Left  *Tree
	Value int
	Right *Tree
}

func WalkSequential(t *Tree, accum *[]int) {
	var stack []*Tree
	curr := t

	for curr != nil || len(stack) > 0 {
		// Reach the leftmost node of the current node
		for curr != nil {
			stack = append(stack, curr)
			curr = curr.Left
		}

		// Pop the top item from the stack
		curr = stack[len(stack)-1]
		stack = stack[:len(stack)-1]

		// Add the current node's value to the result
		*accum = append(*accum, curr.Value)

		// We now need to visit the right subtree
		curr = curr.Right
	}

}

/*
	func SameSeq(t1, t2 *Tree) bool {
		var arr1 []int
		var arr2 []int

		WalkSequential(t1, &arr1)
		WalkSequential(t2, &arr2)

		if len(arr1) != len(arr2) {
			return false
		}
		for index := range arr1 {
			v1 := arr1[index]
			v2 := arr2[index]

			if v1 != v2 {
				return false
			}
		}
		return true

}
*/
func SameSeq(t1, t2 *Tree) bool {
	stack1 := []*Tree{}
	stack2 := []*Tree{}
	curr1 := t1
	curr2 := t2

	for curr1 != nil || curr2 != nil || len(stack1) > 0 || len(stack2) > 0 {
		for curr1 != nil {
			stack1 = append(stack1, curr1)
			curr1 = curr1.Left
		}
		for curr2 != nil {
			stack2 = append(stack2, curr2)
			curr2 = curr2.Left
		}

		if len(stack1) == 0 || len(stack2) == 0 {
			return false
		}
		curr1 = stack1[len(stack1)-1]
		stack1 = stack1[:len(stack1)-1]
		curr2 = stack2[len(stack2)-1]
		stack2 = stack2[:len(stack2)-1]

		if curr1.Value != curr2.Value {
			return false
		}

		curr1 = curr1.Right
		curr2 = curr2.Right
	}

	return len(stack1) == len(stack2)
}

type HashResult struct {
	BSTID int
	Hash  int
}

func Hash(t *Tree, bst_id int) HashResult { //ch chan HashResult,wg *sync.WaitGroup
	// initial hash value
	var in_order_values []int
	WalkSequential(t, &in_order_values)

	hash := 1
	for _, value := range in_order_values {
		new_value := value + 2
		hash = (hash*new_value + new_value) % 1000
	}

	return HashResult{BSTID: bst_id, Hash: hash}
}

func HashChannel(t *Tree, bst_id int, ch chan HashResult) {
	// initial hash value
	var in_order_values []int
	WalkSequential(t, &in_order_values)

	hash := 1
	for _, value := range in_order_values {
		new_value := value + 2
		hash = (hash*new_value + new_value) % 1000
	}
	ch <- HashResult{BSTID: bst_id, Hash: hash}

}

func insert(root *Tree, value int) *Tree {
	if root == nil {
		return &Tree{Value: value}
	}
	if value < root.Value {
		root.Left = insert(root.Left, value)
	} else {
		root.Right = insert(root.Right, value)
	}
	return root
}

func buildTree(values []int) *Tree {
	var root *Tree
	for _, value := range values {
		root = insert(root, value)
	}
	return root
}

func printHashMap(hashMap map[int][]int) {
	for key, value := range hashMap {
		if len(value) > 1 {
			fmt.Printf("%d:", key)
			for _, num := range value {
				fmt.Printf(" %d", num)
			}
			fmt.Println()
		}
	}
}

func printCompare(groups [][]int) {
	for groupId, arr := range groups {
		if len(arr) > 1 {
			fmt.Printf("group %d:", groupId)
			for _, bst_id := range arr {
				fmt.Printf(" %d", bst_id)
			}
			fmt.Println()
		}
	}
}

func groupTrees(bst_equal [][]bool) [][]int {
	visited := make(map[int]int)
	var groups [][]int

	for bst_id1, arr := range bst_equal {
		var equal_arr []int
		equal_arr = append(equal_arr, bst_id1)
		if _, exists := visited[bst_id1]; !exists {
			for bst_id2, bool_val := range arr {
				if bst_id1 != bst_id2 && bool_val {
					equal_arr = append(equal_arr, bst_id2)
					visited[bst_id2] = 1
				}
			}
		}
		if len(equal_arr) > 1 {
			groups = append(groups, equal_arr)
		}
	}
	return groups
}

type dataTask struct {
	hashRes HashResult
}
type dataWorkerPool struct {
	taskChan chan dataTask
	lock     *sync.Mutex
	wg       sync.WaitGroup
	hashMap  *map[int][]int
}

func (wp *dataWorkerPool) placeData() {
	for task := range wp.taskChan {
		bst_id := task.hashRes.BSTID
		hash := task.hashRes.Hash
		wp.lock.Lock()
		if _, exists := (*wp.hashMap)[hash]; exists {
			(*wp.hashMap)[hash] = append((*wp.hashMap)[hash], bst_id)
		} else {
			(*wp.hashMap)[hash] = []int{bst_id}
		}
		wp.lock.Unlock()
		wp.wg.Done()
	}
}

type hashTask struct {
	bst_id int
	t      *Tree
}
type compareTask struct {
	bst_id1   int
	bst_id2   int
	t1        *Tree
	t2        *Tree
	bst_equal *[][]bool
}

type compareWorkerPool struct {
	tasksChan chan compareTask
	wg        sync.WaitGroup
	lock      *sync.Mutex
}

func (wp *compareWorkerPool) compareWorker() {
	for task := range wp.tasksChan {
		t1 := task.t1
		t2 := task.t2
		bst_id1 := task.bst_id1
		bst_id2 := task.bst_id2
		if SameSeq(t1, t2) {
			wp.lock.Lock()
			(*task.bst_equal)[bst_id1][bst_id2] = true
			wp.lock.Unlock()
		}
		wp.wg.Done()
	}
}

type hashWorkerPool struct {
	tasksChan chan hashTask
	results   chan HashResult
	wg        sync.WaitGroup
}

func (wp *hashWorkerPool) hashWorker() {
	for task := range wp.tasksChan {
		HashChannel(task.t, task.bst_id, wp.results)
		wp.wg.Done()
	}
}

func main() {
	//parsing input and building trees
	file, err := os.Open(input)
	if err != nil {
		log.Fatal(err)
	}
	defer file.Close()
	scanner := bufio.NewScanner(file)
	var trees []*Tree
	hashMap := make(map[int][]int)
	var groups [][]int
	for scanner.Scan() {
		line := scanner.Text()
		stringValues := strings.Fields(line)
		var intValues []int

		for _, str := range stringValues {
			val, _ := strconv.Atoi(str)
			intValues = append(intValues, val)
		}
		t := buildTree(intValues)
		trees = append(trees, t)
	}
	if err := scanner.Err(); err != nil {
		log.Fatal(err)
	}

	//start computing hashes
	hashResults := make([]HashResult, 0)
	start := time.Now()
	if hashWorker == 1 {
		//seq

		for bst_id, t := range trees {
			hash := 1
			var in_order_values []int
			WalkSequential(t, &in_order_values)

			for _, value := range in_order_values {
				new_value := value + 2
				hash = (hash*new_value + new_value) % 1000
			}
			hashResults = append(hashResults, HashResult{BSTID: bst_id, Hash: hash})
		}

	} else if hashWorker > 1 {
		//parallel
		/*
			//implementation 1
			ch := make(chan HashResult)
			var wg sync.WaitGroup
			for bst_id, t := range trees {
				wg.Add(1)
				go HashChannel(t, bst_id, ch)
				wg.Done()
			}

			for i := 0; i < len(trees); i++ {
				select {
				case result := <-ch:
					hashResults = append(hashResults, result)
				}
			}

			go func() {
				wg.Wait()
				close(ch)
			}()
		*/

		//implementation 2
		var wg sync.WaitGroup
		ch := make(chan hashTask, len(trees))
		results := make(chan HashResult, len(trees))
		wp := hashWorkerPool{
			tasksChan: ch,
			results:   results,
			wg:        wg,
		}
		//start hashworker number of goroutines
		for i := 0; i < hashWorker; i++ {
			go wp.hashWorker()
		}
		wp.wg.Add(len(trees))
		//send tasks to taskchan
		for bst_id, t := range trees {
			wp.tasksChan <- hashTask{bst_id: bst_id, t: t}
		}
		close(ch)
		go func() {
			wp.wg.Wait()
			close(results)
		}()
		for hashRes := range results {
			hashResults = append(hashResults, hashRes)
		}

	}
	end := time.Now()
	duration := end.Sub(start)
	fmt.Printf("hashTime: %f\n", duration.Seconds())

	if dataWorker == 1 {
		//seq
		for _, result := range hashResults {
			t_bst_id := result.BSTID
			hash := result.Hash
			if _, exists := hashMap[hash]; exists {
				hashMap[hash] = append(hashMap[hash], t_bst_id)
			} else {
				hashMap[hash] = []int{t_bst_id}
			}
		}
	} else if dataWorker > 1 {
		//parallel
		/*
			//implementation 1

				for _, result := range hashResults {
					t_bst_id := result.BSTID
					hash := result.Hash
					if _, exists := hashMap[hash]; exists {
						hashMap[hash] = append(hashMap[hash], t_bst_id)
					} else {
						hashMap[hash] = []int{t_bst_id}
					}
				}
		*/
		//implementation 2
		ch := make(chan dataTask)
		var wg sync.WaitGroup
		var lock sync.Mutex

		dp := dataWorkerPool{
			taskChan: ch,
			lock:     &lock,
			wg:       wg,
			hashMap:  &hashMap,
		}

		for i := 0; i < dataWorker; i++ {
			go dp.placeData()
		}
		dp.wg.Add(len(trees))
		for _, hashRes := range hashResults {
			dp.taskChan <- dataTask{hashRes: hashRes}
		}
		close(ch)
		dp.wg.Wait()
	}

	//printing hashgrouptime at the end
	if dataWorker >= 1 {
		end = time.Now()
		duration = end.Sub(start)
		fmt.Printf("hashGroupTime: %f\n", duration.Seconds())
		printHashMap(hashMap)
	}

	bst_equal := make([][]bool, len(trees))
	for i := range bst_equal {
		bst_equal[i] = make([]bool, len(trees))
	}
	if compWorker == 1 {
		//seq
		start := time.Now()
		seen := make(map[int]int)
		for _, treeArr := range hashMap {
			for _, bst_id1 := range treeArr {
				t1 := trees[bst_id1]
				var equivalent []int
				for _, bst_id2 := range treeArr {
					t2 := trees[bst_id2]
					if _, exists := seen[bst_id2]; !exists && SameSeq(t1, t2) {
						equivalent = append(equivalent, bst_id2)
						seen[bst_id2] = 1
					}
				}
				if len(equivalent) > 1 {
					groups = append(groups, equivalent)
				}
			}
		}
		end := time.Now()
		duration := end.Sub(start)
		fmt.Printf("compareTreeTime: %f\n", duration.Seconds())
		printCompare(groups)
	} else if compWorker > 1 {
		//parallel
		/*
			//implementation 1
			//makes adjacency matrix and initializes to false
			start = time.Now()
			var comp_wg sync.WaitGroup

			//iterate over hashmap and assign values in adjacency matrix
			for _, hashArr := range hashMap {
				for _, bst_id1 := range hashArr {
					t1 := trees[bst_id1]
					for _, bst_id2 := range hashArr {
						t2 := trees[bst_id2]
						comp_wg.Add(1)
						go func(bst_id1 int, bst_id2 int, t1 *Tree, t2 *Tree) {
							defer comp_wg.Done()
							if SameSeq(t1, t2) {
								bst_equal[bst_id1][bst_id2] = true
							}
						}(bst_id1, bst_id2, t1, t2)
					}
				}
			}
			comp_wg.Wait()
			end = time.Now()
			duration = end.Sub(start)
			fmt.Printf("compareTreeTime: %f\n", duration.Seconds())
			groups = groupTrees(bst_equal)
			printCompare(groups)
		*/

		//implementation 2
		start = time.Now()
		var comp_wg sync.WaitGroup
		ch := make(chan compareTask, len(trees))
		var lock sync.Mutex
		cp := compareWorkerPool{
			tasksChan: ch,
			wg:        comp_wg,
			lock:      &lock,
		}
		for i := 0; i < compWorker; i++ {
			go cp.compareWorker()
		}

		//seen := make(map[int]int)
		for _, hashArr := range hashMap {
			for _, bst_id1 := range hashArr {
				t1 := trees[bst_id1]
				//seen[bst_id1] = 1
				for _, bst_id2 := range hashArr {
					//if _, exists := seen[bst_id2]; !exists {
					cp.wg.Add(1)
					t2 := trees[bst_id2]
					cp.tasksChan <- compareTask{bst_id1: bst_id1, bst_id2: bst_id2, t1: t1, t2: t2, bst_equal: &bst_equal}
					//}
				}
			}
		}
		close(ch)
		cp.wg.Wait()

		end = time.Now()
		duration = end.Sub(start)
		fmt.Printf("compareTreeTime: %f\n", duration.Seconds())
		groups = groupTrees(bst_equal)
		printCompare(groups)

	}

}
