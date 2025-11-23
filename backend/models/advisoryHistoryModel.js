import mongoose from "mongoose";

const advisoryHistorySchema = new mongoose.Schema(
  {
    farmer: {
      type: mongoose.Schema.Types.ObjectId,
      ref: "Farmer",
      required: true,
    },
    location: String,
    soilType: String,
    sowingMonth: Number,
    advisory: Object, // Save full AI response
  },
  { timestamps: true }
);

export default mongoose.model("AdvisoryHistory", advisoryHistorySchema);
