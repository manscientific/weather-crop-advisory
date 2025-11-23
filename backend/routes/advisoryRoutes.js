import express from "express";
import { getCropAdvisory } from "../controllers/advisoryController.js";
import { protect } from "../middleware/authMiddleware.js";

const router = express.Router();

router.post("/", protect, getCropAdvisory);

export default router;
