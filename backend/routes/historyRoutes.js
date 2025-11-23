import express from "express";
import { protect } from "../middleware/authMiddleware.js";
import AdvisoryHistory from "../models/advisoryHistoryModel.js";

const router = express.Router();

// GET all history for logged-in farmer
router.get("/", protect, async (req, res) => {
  try {
    const history = await AdvisoryHistory.find({ farmer: req.farmer._id })
      .sort({ createdAt: -1 });

    res.json(history);
  } catch (error) {
    res.status(500).json({ message: "Failed to fetch history" });
  }
});

export default router;
