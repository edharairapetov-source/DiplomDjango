 package main



import (
	"encoding/json"
	"fmt"
	"image"
	"image/color"
	"log"
	"math"
	"math/rand"
	"net/http"
	"os"
	"time"
	"gonum.org/v1/gonum/mat"
	"gonum.org/v1/plot"
	"gonum.org/v1/plot/plotter"
	"gonum.org/v1/plot/vg"
)

// Utility functions
func randFloat64(min, max float64) float64 {
	return min + rand.Float64()*(max-min)
}

// --- Graph Functions ---

type SimpleGraph struct {
	N     int
	Edges map[int]map[int]bool
}

func NewSimpleGraph(n int) *SimpleGraph {
	return &SimpleGraph{
		N:     n,
		Edges: make(map[int]map[int]bool),
	}
}

func (g *SimpleGraph) AddEdge(u, v int) {
	if g.Edges[u] == nil {
		g.Edges[u] = make(map[int]bool)
	}
	if g.Edges[v] == nil {
		g.Edges[v] = make(map[int]bool)
	}
	g.Edges[u][v] = true
	g.Edges[v][u] = true
}

func (g *SimpleGraph) SubgraphDensity(k int) float64 {
	indices := make([]int, g.N)
	for i := 0; i < g.N; i++ {
		indices[i] = i
	}
	combinations := combinationsIndices(indices, k)
	count := 0
	total := 0
	for _, combo := range combinations {
		total++
		if g.isComplete(combo) {
			count++
		}
	}
	if total == 0 {
		return 0
	}
	return float64(count) / float64(total)
}

func (g *SimpleGraph) isComplete(nodes []int) bool {
	for i, u := range nodes {
		for _, v := range nodes[i+1:] {
			if !g.Edges[u][v] {
				return false
			}
		}
	}
	return true
}

func combinationsIndices(arr []int, k int) [][]int {
	var result [][]int
	var comb func(start int, combo []int)
	comb = func(start int, combo []int) {
		if len(combo) == k {
			tmp := make([]int, k)
			copy(tmp, combo)
			result = append(result, tmp)
			return
		}
		for i := start; i < len(arr); i++ {
			comb(i+1, append(combo, arr[i]))
		}
	}
	comb(0, []int{})
	return result
}

func graphDistance(g1, g2 *SimpleGraph, k int) float64 {
	d1 := g1.SubgraphDensity(k)
	d2 := g2.SubgraphDensity(k)
	return math.Abs(d1 - d2)
}

// --- Graphon Visualization ---

func visualizeGraphon(matrix [][]float64, filename string) error {
	size := len(matrix)
	p, err := plot.New()
	if err != nil {
		return err
	}

	img := make([]color.Color, size*size)
	for i := 0; i < size; i++ {
		for j := 0; j < size; j++ {
			val := matrix[i][j]
			if val < 0 {
				val = 0
			}
			if val > 1 {
				val = 1
			}
			gray := uint8(val * 255)
			img[i*size+j] = color.Gray{Y: gray}
		}
	}

	rgbaImg := colorToRGBA(img, size, size)

	imgPlot, err := plotter.NewImage(rgbaImg)
	if err != nil {
		return err
	}
	p.Add(imgPlot)
	p.Title.Text = "Graphon Visualization"
	if err := p.Save(4*vg.Inch, 4*vg.Inch, filename); err != nil {
		return err
	}
	return nil
}

func colorToRGBA(colors []color.Color, width, height int) *image.RGBA {
	img := image.NewRGBA(image.Rect(0, 0, width, height))
	for i, c := range colors {
		x := i % width
		y := i / width
		r, g, b, a := c.RGBA()
		img.SetRGBA(x, y, color.RGBA{
			uint8(r >> 8),
			uint8(g >> 8),
			uint8(b >> 8),
			uint8(a >> 8),
		})
	}
	return img
}

// --- Neural Network (simple implementation) ---

type NeuralNetwork struct {
	W1 *mat.Dense
	b1 *mat.Dense
	W2 *mat.Dense
	b2 *mat.Dense
}

func NewNeuralNetwork(inputDim, hiddenDim, outputDim int) *NeuralNetwork {
	r := rand.New(rand.NewSource(time.Now().UnixNano()))
	W1 := mat.NewDense(inputDim, hiddenDim, nil)
	for i := 0; i < inputDim; i++ {
		for j := 0; j < hiddenDim; j++ {
			W1.Set(i, j, r.NormFloat64()*0.1)
		}
	}
	b1 := mat.NewDense(1, hiddenDim, nil)
	W2 := mat.NewDense(hiddenDim, outputDim, nil)
	for i := 0; i < hiddenDim; i++ {
		for j := 0; j < outputDim; j++ {
			W2.Set(i, j, r.NormFloat64()*0.1)
		}
	}
	b2 := mat.NewDense(1, outputDim, nil)
	return &NeuralNetwork{W1, b1, W2, b2}
}

func (nn *NeuralNetwork) relu(x *mat.Dense) *mat.Dense {
	r, c := x.Dims()
	out := mat.NewDense(r, c, nil)
	for i := 0; i < r; i++ {
		for j := 0; j < c; j++ {
			val := x.At(i, j)
			if val > 0 {
				out.Set(i, j, val)
			} else {
				out.Set(i, j, 0)
			}
		}
	}
	return out
}

func (nn *NeuralNetwork) Forward(x []float64) []float64 {
	xMat := mat.NewDense(1, len(x), x)
	var h mat.Dense
	h.Mul(xMat, nn.W1)
	h.Apply(func(i, j int, v float64) float64 {
		return math.Max(0, v+nn.b1.At(0, j))
	}, &h)

	var out mat.Dense
	out.Mul(&h, nn.W2)
	for j := 0; j < out.RawMatrix().Cols; j++ {
		out.Set(0, j, out.At(0, j)+nn.b2.At(0, j))
	}
	return out.RawRowView(0)
}

// --- Portfolio Optimization ---

func utilityPortfolio(c, expectedReturns []float64, covarianceMatrix [][]float64) float64 {
	expected := 0.0
	for i, val := range expectedReturns {
		expected += val * c[i]
	}
	risk := 0.0
	for i := range c {
		for j := range c {
			risk += c[i] * c[j] * covarianceMatrix[i][j]
		}
	}
	return expected - 0.5*risk
}

func optimizePortfolio(expectedReturns []float64, covarianceMatrix [][]float64) []float64 {
	n := len(expectedReturns)
	// Simple equal weights
	weights := make([]float64, n)
	for i := 0; i < n; i++ {
		weights[i] = 1.0 / float64(n)
	}
	return weights
}

// --- Stock Market Simulation ---

func simulateBlackScholes(S0, T, r, sigma float64, I int) []float64 {
	rng := rand.New(rand.NewSource(time.Now().UnixNano()))
	prices := make([]float64, I)
	for i := 0; i < I; i++ {
		z := rng.NormFloat64()
		price := S0 * math.Exp((r-0.5*sigma*sigma)*T+sigma*math.Sqrt(T)*z)
		prices[i] = price
	}
	return prices
}

func simulateJumpDiffusion(S0, T, r, sigma, lambda, mu, delta float64, I int) []float64 {
	rng := rand.New(rand.NewSource(time.Now().UnixNano()))
	prices := make([]float64, I)
	for i := 0; i < I; i++ {
		z := rng.NormFloat64()
		y := rng.Poisson(lambda * T)
		jump := 1.0
		for j := 0; j < int(y); j++ {
			jumpSize := math.Exp(mu+delta*rng.NormFloat64()) - 1
			jump *= (1 + jumpSize)
		}
		price := S0 * math.Exp((r - lambda*(math.Exp(mu+0.5*delta*delta)-1)-0.5*sigma*sigma)*T+sigma*math.Sqrt(T)*z)
		price *= jump
		prices[i] = price
	}
	return prices
}

// Helper functions
func mean(data []float64) float64 {
	sum := 0.0
	for _, v := range data {
		sum += v
	}
	return sum / float64(len(data))
}

func (s *SimpleGraph) Nodes() []int {
	nodes := make([]int, s.N)
	for i := 0; i < s.N; i++ {
		nodes[i] = i
	}
	return nodes
}

func (s *SimpleGraph) Edges() map[int]map[int]bool {
	return s.Edges
}

// --- API Handlers ---

func main() {
	rand.Seed(time.Now().UnixNano())

	http.HandleFunc("/generate-correlation-matrix", generateCorrelationMatrixHandler)
	http.HandleFunc("/create-graph", createGraphHandler)
	http.HandleFunc("/visualize-graphon", visualizeGraphonHandler)
	http.HandleFunc("/simulate-stock", simulateStockHandler)
	http.HandleFunc("/simulate-jump", simulateJumpHandler)
	http.HandleFunc("/predict-neural", predictNeuralHandler)

	fmt.Println("Starting server at :8080")
	log.Fatal(http.ListenAndServe(":8080", nil))
}

// Request and Response structs

type CorrMatrixRequest struct {
	N             int     `json:"n"`
	CorrThreshold float64 `json:"corr_threshold"`
}

type CorrMatrixResponse struct {
	Matrix [][]float64 `json:"matrix"`
}

func generateCorrelationMatrixHandler(w http.ResponseWriter, r *http.Request) {
	var req CorrMatrixRequest
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		http.Error(w, "Invalid request", http.StatusBadRequest)
		return
	}
	n := req.N
	matrix := make([][]float64, n)
	for i := 0; i < n; i++ {
		matrix[i] = make([]float64, n)
	}
	for i := 0; i < n; i++ {
		for j := i; j < n; j++ {
			if i == j {
				matrix[i][j] = 1
			} else {
				val := randFloat64(-1, 1)
				matrix[i][j] = val
				matrix[j][i] = val
			}
		}
	}
	resp := CorrMatrixResponse{Matrix: matrix}
	json.NewEncoder(w).Encode(resp)
}

type CreateGraphRequest struct {
	N      int     `json:"n"`
	Thresh float64 `json:"threshold"`
}

type CreateGraphResponse struct {
	Edges map[int][]int `json:"edges"`
}

func createGraphHandler(w http.ResponseWriter, r *http.Request) {
	var req CreateGraphRequest
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		http.Error(w, "Invalid request", http.StatusBadRequest)
		return
	}
	g := NewSimpleGraph(req.N)
	// Generate correlation matrix
	corrMatrix := make([][]float64, req.N)
	for i := 0; i < req.N; i++ {
		corrMatrix[i] = make([]float64, req.N)
	}
	for i := 0; i < req.N; i++ {
		for j := i; j < req.N; j++ {
			if i == j {
				corrMatrix[i][j] = 1
			} else {
				val := randFloat64(-1, 1)
				corrMatrix[i][j] = val
				corrMatrix[j][i] = val
			}
		}
	}
	for i := 0; i < req.N; i++ {
		for j := i + 1; j < req.N; j++ {
			if math.Abs(corrMatrix[i][j]) > req.Thresh {
				g.AddEdge(i, j)
			}
		}
	}
	edges := make(map[int][]int)
	for u, neighbors := range g.Edges {
		list := []int{}
		for v := range neighbors {
			list = append(list, v)
		}
		edges[u] = list
	}
	json.NewEncoder(w).Encode(CreateGraphResponse{Edges: edges})
}

type VisualizeGraphonRequest struct {
	Matrix   [][]float64 `json:"matrix"`
	Filename string      `json:"filename"`
}

func visualizeGraphonHandler(w http.ResponseWriter, r *http.Request) {
	var req VisualizeGraphonRequest
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		http.Error(w, "Invalid request", http.StatusBadRequest)
		return
	}
	err := visualizeGraphon(req.Matrix, req.Filename)
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}
	fmt.Fprintf(w, "Graphon visualization saved as %s", req.Filename)
}

type StockSimulationRequest struct {
	S0     float64 `json:"S0"`
	T      float64 `json:"T"`
	R      float64 `json:"r"`
	Sigma  float64 `json:"sigma"`
	I      int     `json:"I"`
	Method string  `json:"method"` // "blackscholes" or "jumpdiffusion"
	Lambda float64 `json:"lambda"` // for jump
	Mu     float64 `json:"mu"`     // for jump
	Delta  float64 `json:"delta"`  // for jump
}

type StockSimulationResponse struct {
	Prices []float64 `json:"prices"`
}

func simulateStockHandler(w http.ResponseWriter, r *http.Request) {
	var req StockSimulationRequest
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		http.Error(w, "Invalid request", http.StatusBadRequest)
		return
	}
	var prices []float64
	if req.Method == "blackscholes" {
		prices = simulateBlackScholes(req.S0, req.T, req.R, req.Sigma, req.I)
	} else if req.Method == "jumpdiffusion" {
		prices = simulateJumpDiffusion(req.S0, req.T, req.R, req.Sigma, req.Lambda, req.Mu, req.Delta, req.I)
	} else {
		http.Error(w, "Invalid method", http.StatusBadRequest)
		return
	}
	resp := StockSimulationResponse{Prices: prices}
	json.NewEncoder(w).Encode(resp)
}

type NeuralPredictRequest struct {
	Data   []float64 `json:"data"`
	Labels []float64 `json:"labels"`
}

type NeuralPredictResponse struct {
	Prediction []float64 `json:"prediction"`
}

func predictNeuralHandler(w http.ResponseWriter, r *http.Request) {
	var req NeuralPredictRequest
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		http.Error(w, "Invalid request", http.StatusBadRequest)
		return
	}
	nn := NewNeuralNetwork(len(req.Data), 16, 4)
	// Dummy training skipped
	// Use a random test sample
	testSample := make([]float64, len(req.Data))
	for i := range testSample {
		testSample[i] = randFloat64(0, 1)
	}
	prediction := nn.Forward(testSample)
	json.NewEncoder(w).Encode(NeuralPredictResponse{Prediction: prediction})
}

