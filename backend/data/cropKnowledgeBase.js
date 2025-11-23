// Simple expert-knowledge base for crops
// You can expand this anytime.

export const cropKnowledgeBase = [
  {
    name: "Rice",
    idealTemp: [24, 35],
    idealRain: [150, 300],          // mm (over season)
    idealHumidity: [60, 90],
    soilTypes: ["clay", "loam"],
    seasons: ["Kharif"],
    sowingMonths: [6, 7, 8],        // Jun–Aug
    harvestMonths: [10, 11, 12],    // Oct–Dec
    riskIndex: 0.4,                 // 0 = low risk, 1 = very risky
    marketDemandIndex: 0.8,         // 0 = low demand, 1 = very high
    waterRequirement: "high",
  },
  {
    name: "Wheat",
    idealTemp: [10, 25],
    idealRain: [20, 100],
    idealHumidity: [40, 60],
    soilTypes: ["loam", "sandy"],
    seasons: ["Rabi"],
    sowingMonths: [11, 12, 1],      // Nov–Jan
    harvestMonths: [3, 4, 5],       // Mar–May
    riskIndex: 0.3,
    marketDemandIndex: 0.9,
    waterRequirement: "medium",
  },
  {
    name: "Maize",
    idealTemp: [18, 27],
    idealRain: [50, 150],
    idealHumidity: [40, 70],
    soilTypes: ["loam", "sandy"],
    seasons: ["Kharif", "Rabi"],
    sowingMonths: [6, 7, 8, 1, 2],
    harvestMonths: [9, 10, 4, 5],
    riskIndex: 0.35,
    marketDemandIndex: 0.7,
    waterRequirement: "medium",
  },
  {
    name: "Sugarcane",
    idealTemp: [20, 35],
    idealRain: [75, 150],
    idealHumidity: [60, 80],
    soilTypes: ["clay", "loam"],
    seasons: ["Annual"],
    sowingMonths: [2, 3, 4],
    harvestMonths: [12, 1],
    riskIndex: 0.5,
    marketDemandIndex: 0.85,
    waterRequirement: "high",
  },
  {
    name: "Potato",
    idealTemp: [10, 20],
    idealRain: [50, 120],
    idealHumidity: [60, 80],
    soilTypes: ["loam", "sandy"],
    seasons: ["Rabi"],
    sowingMonths: [10, 11, 12],
    harvestMonths: [2, 3, 4],
    riskIndex: 0.3,
    marketDemandIndex: 0.75,
    waterRequirement: "medium",
  },
  {
    name: "Millets",
    idealTemp: [20, 32],
    idealRain: [30, 100],
    idealHumidity: [30, 60],
    soilTypes: ["sandy", "loam"],
    seasons: ["Kharif"],
    sowingMonths: [6, 7],
    harvestMonths: [9, 10],
    riskIndex: 0.15,
    marketDemandIndex: 0.6,
    waterRequirement: "low",
  },
  {
    name: "Soybean",
    idealTemp: [20, 30],
    idealRain: [60, 120],
    idealHumidity: [50, 70],
    soilTypes: ["loam"],
    seasons: ["Kharif"],
    sowingMonths: [6, 7],
    harvestMonths: [9, 10],
    riskIndex: 0.35,
    marketDemandIndex: 0.8,
    waterRequirement: "medium",
  },
  {
    name: "Chickpea",
    idealTemp: [10, 25],
    idealRain: [20, 60],
    idealHumidity: [40, 60],
    soilTypes: ["loam", "sandy"],
    seasons: ["Rabi"],
    sowingMonths: [10, 11],
    harvestMonths: [2, 3],
    riskIndex: 0.25,
    marketDemandIndex: 0.7,
    waterRequirement: "low",
  }
];
